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

        # Форматуємо дані
        df = data.reset_index()
        df.columns = ['date', 'price']
        df = df.dropna()
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        # Підключаємось до бази
        conn = sqlite3.connect(DB_PATH)
        
        # ПРИМУСОВИЙ ПЕРЕЗАПИС: 
        # Ми завантажуємо всі нові дані, які дає FRED, і оновлюємо базу
        df.to_sql('gas_prices', conn, if_exists='replace', index=False)
        
        # Отримуємо останню ціну для логів
        last_date = df['date'].iloc[-1]
        last_price = df['price'].iloc[-1]
        
        conn.close()
        print(f"Success! Database updated. Latest price: ${last_price} for {last_date}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    update_database()
