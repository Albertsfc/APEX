"""
APEX - AI Accounts Payable & Receivable Engine
Accounting Sync Plugin (Epic 1)
"""

class AccountingSyncClient:
    def __init__(self, token: str = None):
        self.token = token or "mock_oauth_token"
        
    def sync_invoices_to_erp(self, invoices: list) -> dict:
        """
        Sincroniza faturas criadas/aprovadas no APEX para a plataforma contábil externa.
        """
        # Mocking sync
        return {
            "status": "success",
            "synced_count": len(invoices),
            "external_ids": [f"ext_inv_{i}" for i in range(len(invoices))]
        }
        
    def fetch_chart_of_accounts(self) -> list:
        """
        Busca o plano de contas da plataforma externa para classificar despesas.
        """
        return [
            {"id": "100", "name": "Cash", "type": "Asset"},
            {"id": "200", "name": "Accounts Payable", "type": "Liability"},
            {"id": "500", "name": "Software Subscriptions", "type": "Expense"}
        ]

accounting_client = AccountingSyncClient()
