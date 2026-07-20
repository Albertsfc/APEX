from fastapi import APIRouter, Request

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/inbound")
async def receive_inbound_message(request: Request):
    """Webhook for incoming messages (WhatsApp, Email) to trigger Multichannel Ingestion."""
    payload = await request.json()
    # Mocking ingestion process
    return {"status": "received", "message_id": payload.get("id", "unknown")}
