"""
APEX - AI Accounts Payable & Receivable Engine
CFO Advisory Agent (Epic 4)
"""
from typing import Dict, Any

def run_cfo_advisory(state: Dict[str, Any], dso_forecast: list) -> Dict[str, Any]:
    """
    Agente que consome os dados do DSO e emite recomendações acionáveis de fluxo de caixa em texto natural.
    """
    # Mocking a basic logic for demonstration
    if not dso_forecast:
        return {"cfo_insights": ["Dados insuficientes para gerar insights de fluxo de caixa."]}
        
    insights = []
    # Simple heuristic to mock LLM behavior based on DSO forecast
    if len(dso_forecast) > 0 and dso_forecast[-1].get("yhat", 0) > 45:
        insights.append("DSO projetado está acima de 45 dias. Considere acionar réguas de cobrança antecipadas para os top 5 clientes devedores.")
    else:
        insights.append("Fluxo de caixa saudável. É possível antecipar pagamento a fornecedores chave se houver desconto comercial.")
        
    return {
        "cfo_insights": insights
    }
