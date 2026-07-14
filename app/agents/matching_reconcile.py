"""
APEX - AI Accounts Payable & Receivable Engine
"""
from typing import Dict, Any
from app.skills.match_invoice_payment import match_invoice_to_payment
from app.config import settings

def run_matching_agent(state: Dict[str, Any], afis_transactions: list[dict] = None) -> Dict[str, Any]:
    """Agent responsável por tentar reconciliar a fatura com transações AFIS."""
    if afis_transactions is None:
        afis_transactions = []
        
    invoice_data = state.get("invoice_data", {})
    
    matches = match_invoice_to_payment(invoice_data, afis_transactions)
    best_match = matches[0]
    
    matched_id = best_match.get("afis_transaction_id")
    confidence = best_match.get("confidence_score", 0.0)
    
    requires_human_review = state.get("requires_human_review", False)
    
    if confidence < settings.HUMAN_REVIEW_THRESHOLD:
        requires_human_review = True
        matched_id = None # Não auto-aprova
        
    return {
        "matched_afis_id": matched_id,
        "reconciliation_confidence": confidence,
        "requires_human_review": requires_human_review
    }
