"""
APEX - AI Accounts Payable & Receivable Engine
"""
from typing import Dict, Any
from app.skills.detect_duplicate_invoice import detect_duplicate_invoice
from app.ml.isolation_forest import fraud_detector
from app.config import settings

def run_fraud_agent(state: Dict[str, Any], existing_invoices: list[dict] = None) -> Dict[str, Any]:
    """Agent que roda Isolation Forest e verificação de duplicatas."""
    if existing_invoices is None:
        existing_invoices = []
        
    invoice_data = state.get("invoice_data", {})
    
    # 1. Duplicates
    dup_result = detect_duplicate_invoice(invoice_data, existing_invoices)
    
    # 2. Isolation Forest Anomaly
    fraud_res = fraud_detector.predict_score(invoice_data)
    
    is_duplicate = dup_result.get("is_duplicate", False)
    fraud_score = fraud_res.get("fraud_score", 0.0)
    
    requires_human_review = state.get("requires_human_review", False)
    if is_duplicate or fraud_score > settings.FRAUD_ALERT_THRESHOLD:
        requires_human_review = True
        
    return {
        "is_duplicate": is_duplicate,
        "fraud_score": fraud_score,
        "requires_human_review": requires_human_review
    }
