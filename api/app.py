from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
from prophet import Prophet
import random
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["https://hannesmitterer.github.io"])

def generate_sample_data():
    dates = pd.date_range("2025-01-01", periods=100, freq="D")
    trust_values = [random.uniform(0.5, 1.0) for _ in range(100)]
    harmony_values = [random.uniform(0.5, 1.0) for _ in range(100)]

    df_trust = pd.DataFrame({"ds": dates, "y": trust_values})
    df_harmony = pd.DataFrame({"ds": dates, "y": harmony_values})
    return df_trust, df_harmony

def forecast_data(df):
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=30)  # Forecast for the next 30 days
    forecast = model.predict(future)
    return forecast[['ds', 'yhat']]

@app.route('/api/forecast', methods=['GET'])
def get_forecast():
    df_trust, df_harmony = generate_sample_data()
    trust_forecast = forecast_data(df_trust)
    harmony_forecast = forecast_data(df_harmony)
    trust_forecast_json = trust_forecast.to_dict(orient="records")
    harmony_forecast_json = harmony_forecast.to_dict(orient="records")
    return jsonify({
        "trust_forecast": trust_forecast_json,
        "harmony_forecast": harmony_forecast_json
