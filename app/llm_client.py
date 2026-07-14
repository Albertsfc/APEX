"""
APEX - AI Accounts Payable & Receivable Engine
"""
from typing import Optional, Any
from langchain_anthropic import ChatAnthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import settings
import logging

def get_llm() -> Optional[ChatAnthropic]:
    """Inicializa o cliente Anthropic, ou retorna None (Offline Mode)."""
    if not settings.ANTHROPIC_API_KEY:
        logging.warning("ANTHROPIC_API_KEY not set. APEX will operate in fallback mode without LLM generation.")
        return None
        
    try:
        llm = ChatAnthropic(
            model=settings.LLM_MODEL,
            api_key=settings.ANTHROPIC_API_KEY,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens_to_sample=settings.LLM_MAX_TOKENS,
            timeout=30.0
        )
        return llm
    except Exception as e:
        logging.error(f"Failed to initialize LLM: {e}")
        return None

# Decorator para resiliência de chamadas do LLM na aplicação
retry_llm_call = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda retry_state: logging.warning(f"Retrying LLM call... Attempt {retry_state.attempt_number}")
)
