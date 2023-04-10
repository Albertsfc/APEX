from langchain_anthropic import ChatAnthropic
from app.config import settings
import logging

def get_llm():
    """Inicializa o cliente Anthropic, ou retorna None (Offline Mode)."""
    if not settings.ANTHROPIC_API_KEY:
        logging.warning("ANTHROPIC_API_KEY not set. APEX will operate in fallback mode without LLM generation.")
        return None
        
    try:
        llm = ChatAnthropic(
            model=settings.LLM_MODEL,
            api_key=settings.ANTHROPIC_API_KEY,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens_to_sample=settings.LLM_MAX_TOKENS
        )
        return llm
    except Exception as e:
        logging.error(f"Failed to initialize LLM: {e}")
        return None
