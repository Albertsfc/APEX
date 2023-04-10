DUNNING_STAGES = {
    1: {
        "trigger_days": 7,     # dias após vencimento
        "tone": "friendly",
        "offline_template": "Subject: Friendly Reminder — Invoice {invoice_number}\n\nHi {client_name},\n\nJust a quick note that Invoice {invoice_number} for ${amount:.2f} was due on {due_date}.\nIf you've already sent payment, please disregard this message.\n\nIf you have any questions, please don't hesitate to reach out.\n\nBest regards,\n{company_name}"
    },
    2: {
        "trigger_days": 15,
        "tone": "formal",
        "offline_template": "Subject: Second Notice — Invoice {invoice_number} Past Due\n\nDear {client_name},\n\nThis is a formal reminder that Invoice {invoice_number} for ${amount:.2f}, \noriginally due {due_date}, remains outstanding ({days_overdue} days past due).\n\nPlease arrange payment at your earliest convenience to avoid further action.\n\nSincerely,\n{company_name}"
    },
    3: {
        "trigger_days": 30,
        "tone": "urgent",
        "offline_template": "Subject: URGENT: Final Notice — Invoice {invoice_number}\n\nDear {client_name},\n\nDespite previous notices, Invoice {invoice_number} for ${amount:.2f} \nremains unpaid ({days_overdue} days past due).\n\nFINAL DEMAND: Please remit payment within 5 business days.\nFailure to do so may result in referral to a collections agency \nand/or legal action.\n\n{company_name}"
    },
    4: {
        "trigger_days": 45,
        "tone": "legal",
        "offline_template": "Subject: Notice of Intent to Pursue Legal Action — Invoice {invoice_number}\n\nDear {client_name},\n\nInvoice {invoice_number} for ${amount:.2f} ({days_overdue} days past due)\nhas been referred to our legal department.\n\nUnless full payment is received within 10 business days, we will\ninitiate formal collection proceedings without further notice.\n\n{company_name} Legal Department\n\nThis communication is for informational purposes and is not legal advice."
    },
}

def generate_dunning_email(
    invoice: dict,
    client: dict,
    days_overdue: int,
    stage: int,
    company_name: str,
    llm_client=None
) -> dict:
    """
    Gera e-mail de cobrança personalizado.
    Retorna { "subject": str, "body": str, "tone": str, "stage": int }
    """
    if stage < 1 or stage > 4:
        raise ValueError("Stage must be between 1 and 4")

    stage_info = DUNNING_STAGES[stage]
    tone = stage_info["tone"]

    # Se LLM não disponível/configurado, usa offline template 
    # (Pode ser estendido no Orchestrator)
    template = stage_info["offline_template"]
    
    body = template.format(
        client_name=client.get("name", "Client"),
        invoice_number=invoice.get("invoice_number", "UNKNOWN"),
        amount=invoice.get("total_amount", 0.0),
        due_date=invoice.get("due_date", "UNKNOWN"),
        days_overdue=days_overdue,
        company_name=company_name
    )
    
    subject_line = body.split("\n")[0].replace("Subject: ", "")
    actual_body = "\n".join(body.split("\n")[1:]).strip()

    return {
        "subject": subject_line,
        "body": actual_body,
        "tone": tone,
        "stage": stage
    }
