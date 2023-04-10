from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Caminhos
    BASE_DIR: Path = Path(__file__).parent.parent
    APEX_DB_PATH: str = "apex_ar.db"
    AFIS_DB_PATH: str = "../AFIS/afis_finance.db"   # caminho relativo ao monorepo
    AXIS_DB_PATH: str = "../AXIS/axis_tax.db"        # leitura de classificações
    PDF_STORAGE_PATH: str = "data/invoices"          # pasta local para faturas

    # LLM
    ANTHROPIC_API_KEY: str = ""
    LLM_MODEL: str = "claude-3-5-sonnet-20241022"
    LLM_MAX_TOKENS: int = 2048
    LLM_TEMPERATURE: float = 0.3            # levemente criativo para dunning, mas controlado

    # OCR (Tesseract)
    TESSERACT_CMD: str = "tesseract"        # caminho do binário Tesseract
    OCR_LANG: str = "eng"                   # idioma padrão
    OCR_DPI: int = 300                      # DPI para conversão PDF→imagem

    # ML Models
    ML_MODELS_PATH: str = "app/ml/models"
    FRAUD_CONTAMINATION: float = 0.05       # 5% de contaminação para Isolation Forest
    FRAUD_ALERT_THRESHOLD: float = 0.65     # score acima disso → alerta
    DSO_FORECAST_HORIZON: int = 90          # dias de projeção do DSO

    # Reconciliação
    AUTO_APPROVE_THRESHOLD: float = 0.90    # confidence >= 0.90 → auto-aprovado
    HUMAN_REVIEW_THRESHOLD: float = 0.60    # confidence < 0.60 → manual obrigatório

    # E-mail (dunning)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    EMAIL_FROM: str = ""                    # e-mail de origem das cobranças
    EMAIL_DRY_RUN: bool = True              # True = não envia de fato (modo demo)

    # Dunning (dias após vencimento por estágio)
    DUNNING_STAGE1_DAYS: int = 7
    DUNNING_STAGE2_DAYS: int = 15
    DUNNING_STAGE3_DAYS: int = 30
    DUNNING_STAGE4_DAYS: int = 45

    # Sistema
    HOST: str = "127.0.0.1"
    PORT: int = 8002                        # porta diferente do AFIS (8000) e AXIS (8001)
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
