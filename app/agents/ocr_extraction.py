from typing import Dict, Any
from app.skills.extract_invoice_fields import extract_invoice_fields

def run_ocr_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Agent responsável por orquestrar a extração de dados do PDF."""
    invoice_path = state.get("invoice_path")
    if not invoice_path:
        return {"errors": ["No invoice_path provided"]}
    
    extracted = extract_invoice_fields(invoice_path)
    
    return {
        "invoice_data": {
            "invoice_number": extracted.invoice_number,
            "counterparty_name": extracted.counterparty_name,
            "total_amount": extracted.total_amount,
            "due_date": extracted.due_date,
            "issue_date": extracted.issue_date,
            "raw_text": extracted.raw_text
        },
        "extracted_confidence": extracted.confidence_scores.get("total_amount", 0.0)
    }
