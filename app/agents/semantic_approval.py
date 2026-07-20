"""
APEX - AI Accounts Payable & Receivable Engine
Semantic Approval Agent (Epic 5)
"""
from typing import Dict, Any

def evaluate_invoice(state: Dict[str, Any], invoice_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agente que avalia o histórico do fornecedor e o contexto da fatura para decidir entre AUTO_APPROVE ou MANUAL_REVIEW.
    """
    amount = invoice_data.get("amount", 0)
    vendor = invoice_data.get("vendor", "unknown")
    
    # Mocking LLM semantic validation
    # If amount > 5000 or specific risky keywords exist, route to manual review
    if amount > 5000 or "urgente" in vendor.lower():
        approval_status = "MANUAL_REVIEW"
        reason = "Valor fora do padrão histórico ou contém palavras sensíveis."
    else:
        approval_status = "AUTO_APPROVE"
        reason = "Fatura dentro do padrão comportamental semântico."
        
    return {
        "semantic_approval_status": approval_status,
        "semantic_reason": reason
    }
