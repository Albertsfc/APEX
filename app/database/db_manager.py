"""
APEX - AI Accounts Payable & Receivable Engine
"""
import sqlite3
import logging
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.engine import Engine
from app.config import settings

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection: sqlite3.Connection, connection_record: object) -> None:
    """Configures SQLite to use WAL mode for better concurrency."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

engine = create_engine(
    f"sqlite:///{settings.APEX_DB_PATH}",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db() -> None:
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

def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
