"""
APEX - AI Accounts Payable & Receivable Engine
"""
import pandas as pd
from prophet import Prophet
from app.config import settings
import logging
import warnings

# Suprimir logs chatos do cmdstanpy do prophet
warnings.filterwarnings('ignore')

class DSOForecaster:
    """Previsão de Days Sales Outstanding (DSO) usando o algoritmo Prophet do Meta."""
    
    def __init__(self):
        self.horizon = settings.DSO_FORECAST_HORIZON
        self.model = None

    def generate_forecast(self, historical_dso_df: pd.DataFrame) -> dict:
        """
        Recebe DF com colunas ['ds', 'y'] onde ds = data, y = DSO do dia.
        Gera previsão para os próximos `horizon` dias.
        """
        if historical_dso_df.empty or len(historical_dso_df) < 30:
            logging.warning("Not enough DSO data to forecast (need >= 30 days).")
            return {"forecast": []}

        try:
            self.model = Prophet(yearly_seasonality=True, daily_seasonality=False)
            self.model.fit(historical_dso_df)

            future = self.model.make_future_dataframe(periods=self.horizon)
            forecast = self.model.predict(future)

            # Filtrar apenas o futuro
            max_date = historical_dso_df['ds'].max()
            future_forecast = forecast[forecast['ds'] > max_date]
            
            results = []
            for _, row in future_forecast.iterrows():
                results.append({
                    "date": row['ds'].strftime('%Y-%m-%d'),
                    "forecast_dso": max(0.0, float(row['yhat'])),
                    "lower_bound": max(0.0, float(row['yhat_lower'])),
                    "upper_bound": max(0.0, float(row['yhat_upper'])),
                })
                
            return {"forecast": results}
        except Exception as e:
            logging.error(f"Erro ao prever DSO com Prophet: {e}")
            return {"forecast": []}
        
dso_forecaster = DSOForecaster()
