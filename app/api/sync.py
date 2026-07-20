from fastapi import APIRouter

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/erp")
def force_erp_sync():
    from app.plugins.accounting_sync import accounting_client
    return accounting_client.sync_invoices_to_erp([])

@router.get("/chart-of-accounts")
def get_chart_of_accounts():
    from app.plugins.accounting_sync import accounting_client
    return accounting_client.fetch_chart_of_accounts()
