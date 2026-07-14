"""
APEX - AI Accounts Payable & Receivable Engine
"""
from typing import Dict, Any
from app.skills.generate_dunning_email import generate_dunning_email

def run_dunning_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Agent que dispara e-mails de cobrança baseados no estágio atual."""
    invoice_data = state.get("invoice_data", {})
    days_overdue = invoice_data.get("days_overdue", 0)
    stage = state.get("dunning_stage", 1)
    
    # company_name deveria vir do DB via settings
    company_name = "BP Now - Accounts Receivable"
    
    email_data = generate_dunning_email(
        invoice=invoice_data,
        client={"name": invoice_data.get("counterparty_name", "Client")},
        days_overdue=days_overdue,
        stage=stage,
        company_name=company_name
    )
    
    # Aqui o agente chamaria o EmailConnector para enviar o email de fato
    # (Tratado na API ou Worker)
    
    return {
        "dunning_email_sent": True,
        "dunning_stage": stage,
        "email_data": email_data
    }
