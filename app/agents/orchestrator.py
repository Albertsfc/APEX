"""
APEX - AI Accounts Payable & Receivable Engine
"""
from typing import TypedDict, Dict, Any, List
import logging
from langgraph.graph import StateGraph, END
from app.agents.ocr_extraction import run_ocr_agent
from app.agents.fraud_detection import run_fraud_agent
from app.agents.matching_reconcile import run_matching_agent
from app.agents.afis_sync import run_afis_sync_agent
from app.agents.semantic_approval import evaluate_invoice
from app.agents.cfo_advisory import run_cfo_advisory

# Definição estrita do Estado baseada no SDD
class APEXAgentState(TypedDict, total=False):
    invoice_path: str
    invoice_data: Dict[str, Any]
    extracted_confidence: float
    fraud_score: float
    is_duplicate: bool
    matched_afis_id: int
    reconciliation_confidence: float
    requires_human_review: bool
    dunning_stage: int
    dunning_email_sent: bool
    semantic_approval_status: str
    semantic_reason: str
    cfo_insights: List[str]
    dso_forecast: list
    errors: List[str]

# Nós
def ocr_node(state: APEXAgentState) -> Dict[str, Any]:
    try:
        res = run_ocr_agent(state)
        return {
            "invoice_data": res.get("invoice_data", {}),
            "extracted_confidence": res.get("extracted_confidence", 0.0),
            "errors": state.get("errors", []) + res.get("errors", [])
        }
    except Exception as e:
        logging.error(f"OCR Node Error: {e}")
        return {"errors": state.get("errors", []) + [f"OCR Error: {str(e)}"], "requires_human_review": True}

def fraud_node(state: APEXAgentState) -> Dict[str, Any]:
    try:
        res = run_fraud_agent(state)
        return {
            "fraud_score": res.get("fraud_score", 0.0),
            "is_duplicate": res.get("is_duplicate", False),
            "requires_human_review": res.get("requires_human_review", False)
        }
    except Exception as e:
        logging.error(f"Fraud Node Error: {e}")
        return {"errors": state.get("errors", []) + [f"Fraud Check Error: {str(e)}"], "requires_human_review": True}

def match_node(state: APEXAgentState) -> Dict[str, Any]:
    try:
        res = run_matching_agent(state)
        return {
            "matched_afis_id": res.get("matched_afis_id"),
            "reconciliation_confidence": res.get("reconciliation_confidence", 0.0),
            "requires_human_review": state.get("requires_human_review") or res.get("requires_human_review", False)
        }
    except Exception as e:
        logging.error(f"Match Node Error: {e}")
        return {"errors": state.get("errors", []) + [f"Match Error: {str(e)}"], "requires_human_review": True}

def afis_sync_node(state: APEXAgentState) -> Dict[str, Any]:
    try:
        run_afis_sync_agent(state)
        return {}
    except Exception as e:
        logging.error(f"AFIS Sync Node Error: {e}")
        return {"errors": state.get("errors", []) + [f"AFIS Sync Error: {str(e)}"]}

def semantic_approval_node(state: APEXAgentState) -> Dict[str, Any]:
    try:
        res = evaluate_invoice(state, state.get("invoice_data", {}))
        return {
            "semantic_approval_status": res.get("semantic_approval_status"),
            "semantic_reason": res.get("semantic_reason"),
            "requires_human_review": res.get("semantic_approval_status") == "MANUAL_REVIEW"
        }
    except Exception as e:
        return {"errors": state.get("errors", []) + [f"Semantic Error: {str(e)}"], "requires_human_review": True}

def cfo_advisory_node(state: APEXAgentState) -> Dict[str, Any]:
    try:
        # Pass current dso_forecast to CFO
        res = run_cfo_advisory(state, state.get("dso_forecast", []))
        return {"cfo_insights": res.get("cfo_insights", [])}
    except Exception as e:
        return {"errors": state.get("errors", []) + [f"CFO Error: {str(e)}"]}

def human_review_node(state: APEXAgentState) -> Dict[str, Any]:
    return {"requires_human_review": True}

# Lógica de roteamento
def route_after_ocr(state: APEXAgentState) -> str:
    if state.get("extracted_confidence", 0.0) < 0.6 or "OCR Error" in "".join(state.get("errors", [])):
        return "human_review"
    return "fraud_check"

def route_after_fraud(state: APEXAgentState) -> str:
    if state.get("is_duplicate") or state.get("fraud_score", 0.0) > 0.65 or "Fraud Check Error" in "".join(state.get("errors", [])):
        return "human_review"
    return "reconcile"

# Orquestração (Grafo)
workflow = StateGraph(APEXAgentState)

workflow.add_node("ocr", ocr_node)
workflow.add_node("fraud", fraud_node)
workflow.add_node("match", match_node)
workflow.add_node("semantic_approval", semantic_approval_node)
workflow.add_node("sync", afis_sync_node)
workflow.add_node("cfo_advisory", cfo_advisory_node)
workflow.add_node("human_review", human_review_node)

workflow.set_entry_point("ocr")

# Regras de fluxo dinâmico
workflow.add_conditional_edges("ocr", route_after_ocr, {"human_review": "human_review", "fraud_check": "fraud"})
workflow.add_conditional_edges("fraud", route_after_fraud, {"human_review": "human_review", "reconcile": "match"})
workflow.add_edge("match", "semantic_approval")

def route_after_semantic(state: APEXAgentState) -> str:
    if state.get("semantic_approval_status") == "MANUAL_REVIEW":
        return "human_review"
    return "sync"

workflow.add_conditional_edges("semantic_approval", route_after_semantic, {"human_review": "human_review", "sync": "sync"})
workflow.add_edge("sync", "cfo_advisory")
workflow.add_edge("cfo_advisory", END)
workflow.add_edge("human_review", END)

apex_orchestrator = workflow.compile()
