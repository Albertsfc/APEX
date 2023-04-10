from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.db_manager import get_db

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/ar-aging")
def get_ar_aging(db: Session = Depends(get_db)):
    """Mock for AR aging report based on invoices table."""
    # O ideal seria um GROUP BY real com DATEDIFF, mas como mock para o SDD:
    return {
        "0-30": 15000.0,
        "31-60": 5000.0,
        "61-90": 2000.0,
        "90+": 1000.0,
        "total": 23000.0
    }
