"""
APEX - AI Accounts Payable & Receivable Engine
"""
import sqlite3
import logging
from pathlib import Path
from app.config import settings

class AXISReader:
    """Plugin de leitura do banco de dados do AXIS Tax Intelligence System."""

    def __init__(self):
        self.db_path = Path(settings.AXIS_DB_PATH).resolve()

    def is_connected(self) -> bool:
        return self.db_path.exists()

    def get_classified_transactions(
        self,
        afis_transaction_ids: list[int]
    ) -> list[dict]:
        """
        Busca classificações IRS do AXIS para transações específicas do AFIS.
        Retorna: afis_transaction_id, irs_category, irs_code, deductible, schedule_line
        """
        if not self.is_connected() or not afis_transaction_ids:
            return []

        placeholders = ",".join("?" * len(afis_transaction_ids))
        query = f"""
            SELECT afis_transaction_id, irs_category, irs_code,
                   deductible, schedule_line, confidence_score
            FROM classified_transactions
            WHERE afis_transaction_id IN ({placeholders})
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, afis_transaction_ids)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"AXIS read error: {e}")
            return []
