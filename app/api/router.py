from fastapi import APIRouter

from .invoices import router as invoices_router
from .reconciliation import router as reconciliation_router
from .dunning import router as dunning_router
from .fraud import router as fraud_router
from .forecast import router as forecast_router
from .reports import router as reports_router
from .system import router as system_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(invoices_router)
api_router.include_router(reconciliation_router)
api_router.include_router(dunning_router)
api_router.include_router(fraud_router)
api_router.include_router(forecast_router)
api_router.include_router(reports_router)
api_router.include_router(system_router)
