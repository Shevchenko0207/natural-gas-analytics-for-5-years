import os
import pandas as pd
from fredapi import Fred
from datetime import datetime
import sqlite3
from pathlib import Path

def update_database():
    CURRENT_DIR = Path(__file__).parent.resolve()
    PROJECT_ROOT = CURRENT_DIR.parent
    DB_PATH = PROJECT_ROOT / 'energy_data.db'
    
    api_key = os.getenv('FRED_API_KEY')
    if not api_key:
        print("Error: FRED_API_KEY not found")
        return

    fred = Fred(api_key=api_key)
    
    try:
        print("Fetching data from FRED...")
        series_id = 'DHHNGSP'
        data = fred.get_series(series_id)
        
        if data.empty:
            print("No data received from FRED")
            return

        df = data.reset_index()
        df.columns = ['observation_date', 'current_price'] 
        df = df.dropna()
        
        # 1. Часові ознаки (виправляємо 'month_num')
        df['observation_date'] = pd.to_datetime(df['observation_date'])
        df['month_num'] = df['observation_date'].dt.month
        df['day_of_week'] = df['observation_date'].dt.dayofweek
        df['year'] = df['observation_date'].dt.year
        
        # 2. Лаги (для моделі)
        for i in [1, 2, 3, 7, 14]:
            df[f'lag_{i}'] = df['current_price'].shift(i)
        
        # 3. Ковзні середні (виправляємо 'moving_avg_30')
        df['moving_avg_7'] = df['current_price'].transform(lambda x: x.rolling(window=7).mean())
        df['moving_avg_30'] = df['current_price'].transform(lambda x: x.rolling(window=30).mean())
        
        # Додаткові технічні назви, які можуть бути в app.py
        df['rolling_mean_7'] = df['moving_avg_7']
        df['rolling_mean_30'] = df['moving_avg_30']
        
        # Видаляємо NaN та форматуємо дату назад у рядок для SQLite
        df = df.dropna()
        df['observation_date'] = df['observation_date'].dt.strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(DB_PATH)
        df.to_sql('gas_prices_ml_7d', conn, if_exists='replace', index=False)
        
        last_date = df['observation_date'].iloc[-1]
        last_price = df['current_price'].iloc[-1]
        
        conn.close()
        print(f"Success! Database updated with full ML features. Latest: ${last_price}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    update_database()
