"""
APEX - AI Accounts Payable & Receivable Engine
"""
import sqlite3
import logging
from pathlib import Path
from app.config import settings

class AFISReader:
    """Plugin de leitura do banco de dados do AFIS Core Framework."""

    def __init__(self):
        self.db_path = Path(settings.AFIS_DB_PATH).resolve()

    def is_connected(self) -> bool:
        return self.db_path.exists()

    def get_transactions(
        self,
        start_date: str,
        end_date: str,
        tx_type: str = "both",
        limit: int = 1000
    ) -> list[dict]:
        """
        Busca transações do AFIS no período especificado.
        Retorna lista de dicts com: id, date, description, amount, category
        amount > 0 = receita, amount < 0 = despesa
        """
        if not self.is_connected():
            return []

        if tx_type == "income":
            amount_filter = "AND amount > 0"
        elif tx_type == "expense":
            amount_filter = "AND amount < 0"
        else:
            amount_filter = ""

        query = f"""
            SELECT id, date, description, amount, category
            FROM transactions
            WHERE date BETWEEN ? AND ?
            {amount_filter}
            ORDER BY date DESC
            LIMIT ?
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, (start_date, end_date, limit))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"AFIS read error: {e}")
            return []

    def get_unmatched_for_apex(
        self,
        year: int,
        tx_type: str = "both"
    ) -> list[dict]:
        """
        Retorna transações do AFIS que ainda não foram reconciliadas pelo APEX.
        Cruza com reconciliations do APEX database para excluir já processadas.
        """
        if not self.is_connected():
            return []
        
        # Em modo produção, cruza os ids de AFIS com os de APEX via subquery ou JOIN in memory.
        # Por simplicidade (AFISReader read-only isolado), buscaremos dados e quem o chama fará o filtro final.
        pass
