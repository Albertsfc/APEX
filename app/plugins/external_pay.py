"""
APEX - AI Accounts Payable & Receivable Engine
External Payment Gateway Plugin (Epic 2)
"""

class ExternalPayClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "mock_key"
        
    def create_payment_intent(self, amount: float, currency: str, invoice_id: str) -> dict:
        """
        Gera um link de pagamento em outra plataforma para enviar ao cliente.
        """
        # Mocking an external API call
        return {
            "status": "success",
            "invoice_id": invoice_id,
            "payment_link": f"https://pay.external-platform.com/pay/{invoice_id}?amt={amount}",
            "intent_id": "pi_mock_12345"
        }
        
    def schedule_ach_transfer(self, vendor_id: str, amount: float, date: str) -> dict:
        """
        Agenda uma transferência ACH de saída para um fornecedor via plataforma parceira.
        """
        return {
            "status": "scheduled",
            "vendor_id": vendor_id,
            "amount": amount,
            "transfer_date": date,
            "transfer_id": "tr_mock_67890"
        }

pay_client = ExternalPayClient()
