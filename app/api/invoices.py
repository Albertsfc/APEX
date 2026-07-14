"""
APEX - AI Accounts Payable & Receivable Engine
"""
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.db_manager import get_db, SessionLocal
from app.database import models
from app.plugins.pdf_storage import PDFStorage
from app.agents.orchestrator import apex_orchestrator
from typing import Optional, List, Dict, Any
import os
import logging

router = APIRouter(prefix="/invoices", tags=["Invoices"])

def process_invoice_pipeline(file_path: str) -> None:
    """Executes the invoice pipeline in a background task."""
    state: Dict[str, Any] = {"invoice_path": file_path, "errors": []}
    final_state = apex_orchestrator.invoke(state)
    
    data = final_state.get("invoice_data", {})
    if data:
        try:
            with SessionLocal() as db:
                # Salva a fatura no banco de dados com os dados extraídos
                inv = models.Invoice(
                    invoice_number=data.get("invoice_number", "UNKNOWN"),
                    invoice_type="AP", # default assumption for uploads
                    counterparty_name=data.get("counterparty_name", "UNKNOWN"),
                    issue_date=data.get("issue_date", "2026-01-01"),
                    due_date=data.get("due_date", "2026-01-30"),
                    amount=data.get("total_amount", 0.0),
                    total_amount=data.get("total_amount", 0.0),
                    source_path=file_path,
                    ocr_confidence=final_state.get("extracted_confidence", 0.0),
                    fraud_score=final_state.get("fraud_score", 0.0),
                    is_duplicate=bool(final_state.get("is_duplicate")),
                    requires_human_review=bool(final_state.get("requires_human_review"))
                )
                db.add(inv)
                db.commit()
        except Exception as e:
            logging.error(f"Failed to save invoice from pipeline: {e}")

@router.post("/upload")
async def upload_invoice(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
) -> Dict[str, str]:
    # Salvar o arquivo recebido temporariamente
    os.makedirs("data/examples", exist_ok=True)
    temp_path = f"data/examples/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
        
    storage = PDFStorage()
    final_path = storage.store_pdf(temp_path)
    
    if final_path:
        background_tasks.add_task(process_invoice_pipeline, final_path)
        return {"status": "accepted", "message": "Invoice uploaded and pipeline started."}
    return {"status": "error", "message": "Failed to store PDF."}

@router.get("/")
def list_invoices(
    status: Optional[str] = None, 
    type: Optional[str] = None, 
    db: Session = Depends(get_db), 
    limit: int = 50
) -> List[models.Invoice]:
    query = db.query(models.Invoice)
    if status:
        query = query.filter(models.Invoice.status == status)
    if type:
        query = query.filter(models.Invoice.invoice_type == type)
    return query.order_by(models.Invoice.created_at.desc()).limit(limit).all()
