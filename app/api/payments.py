from fastapi import APIRouter

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/intent")
def create_payment_intent(amount: float, invoice_id: str):
    from app.plugins.external_pay import pay_client
    return pay_client.create_payment_intent(amount, "USD", invoice_id)

@router.post("/schedule")
def schedule_payment(vendor_id: str, amount: float, date: str):
    from app.plugins.external_pay import pay_client
    return pay_client.schedule_ach_transfer(vendor_id, amount, date)
