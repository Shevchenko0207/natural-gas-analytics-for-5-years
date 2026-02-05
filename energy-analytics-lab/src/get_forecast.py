import sqlite3
import pandas as pd
import joblib

def get_live_forecast():
    # Завантажуємо моделі
    m1 = joblib.load('models/model_1d.joblib')
    m7 = joblib.load('models/model_7d.joblib')

    conn = sqlite3.connect('energy_data.db')
    # Беремо найсвіжіші дані з бази
    last_data = pd.read_sql_query("SELECT * FROM gas_prices_ml_7d ORDER BY observation_date DESC LIMIT 1", conn)
    conn.close()

    # Підготовка вхідних даних
    features_1d = last_data[['lag_1', 'lag_7', 'moving_avg_30', 'month_num']]
    features_7d = last_data[['current_price', 'lag_1', 'lag_7', 'moving_avg_30', 'month_num']]

    pred1 = m1.predict(features_1d)[0]
    pred7 = m7.predict(features_7d)[0]

    print(f"--- ШВИДКИЙ ЕНЕРГО-ПРОГНОЗ ---")
    print(f"Поточна ціна: ${last_data['current_price'].values[0]:.2f}")
    print(f"Прогноз на завтра: ${pred1:.2f}")
    print(f"Прогноз через 7 днів: ${pred7:.2f}")

if __name__ == "__main__":
    get_live_forecast()
