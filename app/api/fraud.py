from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db_manager import get_db
from app.database import models

router = APIRouter(prefix="/fraud", tags=["Fraud"])

@router.get("/alerts")
def list_fraud_alerts(status: str = "open", db: Session = Depends(get_db), limit: int = 50):
    query = db.query(models.FraudAlert)
    if status:
        query = query.filter(models.FraudAlert.status == status)
    return query.limit(limit).all()

@router.post("/{alert_id}/resolve")
def resolve_fraud_alert(alert_id: int, resolution: str, db: Session = Depends(get_db)):
    alert = db.query(models.FraudAlert).filter(models.FraudAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.status = "resolved"
    alert.resolution_notes = resolution
    
    # Se resolvido, remove a flag da invoice
    if resolution.lower() == "false_positive":
        invoice = db.query(models.Invoice).filter(models.Invoice.id == alert.invoice_id).first()
        if invoice:
            invoice.requires_human_review = 0
            
    db.commit()
    return {"status": "success", "message": "Alert resolved"}
