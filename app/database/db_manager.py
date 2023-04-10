import sqlite3
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(
    f"sqlite:///{settings.APEX_DB_PATH}",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """Initializes the APEX database using the raw schema.sql if it doesn't exist."""
    db_path = Path(settings.APEX_DB_PATH)
    if not db_path.exists():
        logging.info("Initializing APEX database from schema.sql...")
        schema_path = Path(__file__).parent / "schema.sql"
        if schema_path.exists():
            with sqlite3.connect(db_path) as conn:
                with open(schema_path, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
            logging.info("APEX database created successfully.")
        else:
            logging.error(f"schema.sql not found at {schema_path}")

def get_db():
    """Dependency for FastAPI endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
