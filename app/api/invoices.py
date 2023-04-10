from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.db_manager import get_db
from app.database import models
from app.plugins.pdf_storage import PDFStorage
from app.agents.orchestrator import apex_orchestrator
import os

router = APIRouter(prefix="/invoices", tags=["Invoices"])

def process_invoice_pipeline(file_path: str, db: Session):
    # Roda o LangGraph
    state = {"invoice_path": file_path, "errors": []}
    final_state = apex_orchestrator.invoke(state)
    
    data = final_state.get("invoice_data", {})
    if data:
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
            is_duplicate=1 if final_state.get("is_duplicate") else 0,
            requires_human_review=1 if final_state.get("requires_human_review") else 0
        )
        db.add(inv)
        db.commit()

@router.post("/upload")
async def upload_invoice(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Salvar o arquivo recebido temporariamente
    os.makedirs("data/examples", exist_ok=True)
    temp_path = f"data/examples/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
        
    storage = PDFStorage()
    final_path = storage.store_pdf(temp_path)
    
    if final_path:
        background_tasks.add_task(process_invoice_pipeline, final_path, db)
        return {"status": "accepted", "message": "Invoice uploaded and pipeline started."}
    return {"status": "error", "message": "Failed to store PDF."}

@router.get("/")
def list_invoices(status: str = None, type: str = None, db: Session = Depends(get_db), limit: int = 50):
    query = db.query(models.Invoice)
    if status:
        query = query.filter(models.Invoice.status == status)
    if type:
        query = query.filter(models.Invoice.invoice_type == type)
    return query.order_by(models.Invoice.created_at.desc()).limit(limit).all()
