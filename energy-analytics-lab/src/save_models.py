import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

def save_trained_models():
    # Створюємо папку для моделей, якщо її немає
    os.makedirs('models', exist_ok=True)
    conn = sqlite3.connect('energy_data.db')

    # Модель на 1 день
    df1 = pd.read_sql_query("SELECT * FROM gas_prices_ml", conn).dropna()
    m1 = RandomForestRegressor(n_estimators=100, random_state=42)
    m1.fit(df1[['lag_1', 'lag_7', 'moving_avg_30', 'month_num']], df1['target_price'])
    joblib.dump(m1, 'models/model_1d.joblib')

    # Модель на 7 днів
    df7 = pd.read_sql_query("SELECT * FROM gas_prices_ml_7d", conn).dropna()
    m7 = RandomForestRegressor(n_estimators=200, random_state=42)
    m7.fit(df7[['current_price', 'lag_1', 'lag_7', 'moving_avg_30', 'month_num']], df7['target_7d'])
    joblib.dump(m7, 'models/model_7d.joblib')

    conn.close()
    print("Обидві моделі успішно збережені в папку models/")

if __name__ == "__main__":
    save_trained_models()
