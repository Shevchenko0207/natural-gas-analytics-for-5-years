import os
import pandas as pd
from fredapi import Fred
from datetime import datetime
import sqlite3
from pathlib import Path

def update_database():
    # Налаштування шляхів
    CURRENT_DIR = Path(__file__).parent.resolve()
    PROJECT_ROOT = CURRENT_DIR.parent
    DB_PATH = PROJECT_ROOT / 'energy_data.db'
    
    # Отримання API ключа
    api_key = os.getenv('FRED_API_KEY')
    if not api_key:
        print("Error: FRED_API_KEY not found")
        return

    fred = Fred(api_key=api_key)
    
    try:
        # Отримуємо дані Henry Hub Natural Gas Spot Price
        print("Fetching data from FRED...")
        series_id = 'DHHNGSP'
        data = fred.get_series(series_id)
        
        if data.empty:
            print("No data received from FRED")
            return

        # Форматуємо основні дані
        df = data.reset_index()
        df.columns = ['observation_date', 'current_price'] 
        df = df.dropna()
        
        # Створюємо лаги та фічі, які очікує модель в app.py
        # lag_1 - ціна вчора, lag_7 - ціна тиждень тому тощо.
        df['lag_1'] = df['current_price'].shift(1)
        df['lag_2'] = df['current_price'].shift(2)
        df['lag_3'] = df['current_price'].shift(3)
        df['lag_7'] = df['current_price'].shift(7)
        
        # Розраховуємо ковзне середнє (якщо модель його використовує)
        df['rolling_mean_7'] = df['current_price'].transform(lambda x: x.rolling(window=7).mean())
        
        # Чистимо NaN, які з'явилися після створення лагів
        df = df.dropna()
        
        # Форматуємо дату після розрахунків
        df['observation_date'] = pd.to_datetime(df['observation_date']).dt.strftime('%Y-%m-%d')
        
        # Підключаємось до бази
        conn = sqlite3.connect(DB_PATH)
        
        # Записуємо в таблицю з повною структурою
        df.to_sql('gas_prices_ml_7d', conn, if_exists='replace', index=False)
        
        # Отримуємо дані для логів (виправлено назви колонок)
        last_date = df['observation_date'].iloc[-1]
        last_price = df['current_price'].iloc[-1]
        
        conn.close()
        print(f"Success! Database updated with ML features. Latest: ${last_price} for {last_date}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    update_database()
