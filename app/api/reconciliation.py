"""
APEX - AI Accounts Payable & Receivable Engine
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db_manager import get_db
from app.database import models

router = APIRouter(prefix="/reconciliation", tags=["Reconciliation"])

@router.get("/pending")
def list_pending_reconciliations(db: Session = Depends(get_db), limit: int = 50):
    query = db.query(models.Reconciliation).filter(models.Reconciliation.status == "pending_review")
    return query.limit(limit).all()

@router.post("/{reconciliation_id}/approve")
def approve_reconciliation(reconciliation_id: int, db: Session = Depends(get_db)):
    rec = db.query(models.Reconciliation).filter(models.Reconciliation.id == reconciliation_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
        
    rec.status = "approved"
    rec.reviewed_by_human = 1
    
    # Update related invoice
    invoice = db.query(models.Invoice).filter(models.Invoice.id == rec.invoice_id).first()
    if invoice:
        invoice.status = "paid"
        invoice.afis_transaction_id = rec.afis_transaction_id
        
    db.commit()
    return {"status": "success", "message": "Reconciliation approved"}
