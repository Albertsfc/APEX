"""
APEX - AI Accounts Payable & Receivable Engine
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db_manager import get_db
from app.database import models
from app.agents.dunning_communication import run_dunning_agent
from datetime import datetime

router = APIRouter(prefix="/dunning", tags=["Dunning"])

@router.get("/campaigns")
def list_campaigns(db: Session = Depends(get_db), limit: int = 50):
    return db.query(models.DunningCampaign).limit(limit).all()

@router.post("/trigger-stage")
def trigger_dunning_stage(invoice_id: int, stage: int, db: Session = Depends(get_db)):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    # Chama o Agente de Dunning
    state = {
        "invoice_data": {
            "invoice_number": invoice.invoice_number,
            "counterparty_name": invoice.counterparty_name,
            "total_amount": invoice.total_amount,
            "due_date": str(invoice.due_date),
            "days_overdue": (datetime.utcnow().date() - invoice.due_date).days if invoice.due_date else 0
        },
        "dunning_stage": stage
    }
    
    result = run_dunning_agent(state)
    
    # Registra no BD
    campaign = models.DunningCampaign(
        invoice_id=invoice.id,
        campaign_stage=stage,
        tone=result["email_data"]["tone"],
        email_subject=result["email_data"]["subject"],
        email_body=result["email_data"]["body"],
        status="sent" if result.get("dunning_email_sent") else "draft"
    )
    db.add(campaign)
    db.commit()
    
    return {"status": "success", "campaign_stage": stage, "email_data": result["email_data"]}
