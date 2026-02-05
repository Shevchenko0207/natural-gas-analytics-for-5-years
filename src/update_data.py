import pandas as pd
import sqlite3
import os
from fredapi import Fred
from datetime import datetime

# Налаштування
API_KEY = os.getenv('FRED_API_KEY')
DB_PATH = os.path.join(os.path.dirname(__file__), '../energy_data.db')

def update_gas_prices():
    fred = Fred(api_key=API_KEY)
    # Отримуємо останню ціну Henry Hub (Daily)
    data = fred.get_series('DHHNGSP')
    latest_date = data.index[-1]
    latest_price = data.iloc[-1]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Додаємо лише якщо такої дати ще немає
    date_str = latest_date.strftime('%Y-%m-%d')
    cursor.execute("INSERT OR IGNORE INTO gas_prices (date, price) VALUES (?, ?)", (date_str, latest_price))

    conn.commit()
    conn.close()
    print(f"Updated: {date_str} - ${latest_price}")

if __name__ == "__main__":
    update_gas_prices()
