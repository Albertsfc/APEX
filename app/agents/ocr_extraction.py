"""
APEX - AI Accounts Payable & Receivable Engine
"""
from typing import Dict, Any
from app.skills.extract_invoice_fields import extract_invoice_fields

def run_ocr_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Agent responsável por orquestrar a extração de dados do PDF."""
    invoice_path = state.get("invoice_path")
    if not invoice_path:
        return {"errors": ["No invoice_path provided"]}
        
    use_vision_llm = state.get("use_vision_llm", False)
    if use_vision_llm:
        # Mocking Vision LLM processing
        extracted_data = {
            "invoice_number": "VIS-999",
            "counterparty_name": "Vision Extracted Vendor",
            "total_amount": 1234.56,
            "due_date": "2026-08-01",
            "issue_date": "2026-07-20",
            "raw_text": "Extracted via LLM Multimodal"
        }
        confidence = 0.99
    else:
        extracted = extract_invoice_fields(invoice_path)
        extracted_data = {
            "invoice_number": extracted.invoice_number,
            "counterparty_name": extracted.counterparty_name,
            "total_amount": extracted.total_amount,
            "due_date": extracted.due_date,
            "issue_date": extracted.issue_date,
            "raw_text": extracted.raw_text
        }
        confidence = extracted.confidence_scores.get("total_amount", 0.0)
    
    return {
        "invoice_data": extracted_data,
        "extracted_confidence": confidence
    }
