from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/health")
def health_check():
    """Valida se a aplicação e a API estão respondendo."""
    return {"status": "ok", "service": "APEX AI Engine"}

@router.get("/config")
def get_config():
    """Retorna configurações não-sensíveis."""
    safe_config = {
        "HOST": settings.HOST,
        "PORT": settings.PORT,
        "LLM_MODEL": settings.LLM_MODEL,
        "DEBUG": settings.DEBUG,
        "AUTO_APPROVE_THRESHOLD": settings.AUTO_APPROVE_THRESHOLD,
        "FRAUD_ALERT_THRESHOLD": settings.FRAUD_ALERT_THRESHOLD,
        "DSO_FORECAST_HORIZON": settings.DSO_FORECAST_HORIZON
    }
    return safe_config
