import numpy as np
from sklearn.ensemble import IsolationForest
import pandas as pd
from app.config import settings
import logging

class FraudDetector:
    """Detecta anomalias em faturas (fraude) usando Isolation Forest."""
    
    def __init__(self):
        self.contamination = settings.FRAUD_CONTAMINATION
        self.model = IsolationForest(contamination=self.contamination, random_state=42)
        self.is_fitted = False

    def fit(self, df: pd.DataFrame):
        """Treina o Isolation Forest com base no histórico."""
        if df.empty or len(df) < 10:
            logging.info("Dados insuficientes para treinar Isolation Forest.")
            return
            
        features = self._extract_features(df)
        self.model.fit(features)
        self.is_fitted = True

    def predict_score(self, invoice_dict: dict) -> dict:
        """Retorna o score de fraude (0 a 1) e as features sinalizadas."""
        if not self.is_fitted:
            return {"fraud_score": 0.0, "features_flagged": []}

        try:
            df = pd.DataFrame([invoice_dict])
            features = self._extract_features(df)
            
            # decision_function retorna valores onde menores (negativos) são anomalias
            score_raw = self.model.decision_function(features)[0]
            
            # Normalizando para 0-1 (1 sendo mais fraudulento/anômalo)
            # O IsolationForest raw score costuma ficar entre -0.5 e 0.5
            score_norm = 0.5 - (score_raw / 2)
            score_norm = max(0.0, min(1.0, score_norm))
            
            flagged = []
            if score_norm > settings.FRAUD_ALERT_THRESHOLD:
                flagged.append("anomaly_detected")

            return {"fraud_score": float(score_norm), "features_flagged": flagged}
        except Exception as e:
            logging.error(f"Erro ao calcular fraud score: {e}")
            return {"fraud_score": 0.0, "features_flagged": []}

    def _extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extrai as features numéricas para o modelo."""
        X = pd.DataFrame()
        X['amount'] = df.get('total_amount', pd.Series([0.0])).fillna(0.0).astype(float)
        # Mais features (ex: tempo até vencimento, desvios da média do fornecedor) 
        # poderiam ser adicionadas aqui.
        return X

fraud_detector = FraudDetector()
