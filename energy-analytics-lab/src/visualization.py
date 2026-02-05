import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

def generate_report():
    conn = sqlite3.connect('energy_data.db')

    # Завантажуємо обидві таблиці для порівняння
    df_raw = pd.read_sql_query("SELECT observation_date, price_usd FROM gas_prices_raw", conn)
    df_clean = pd.read_sql_query("SELECT observation_date, price_cleaned FROM gas_prices_final", conn)

    # Конвертуємо дати та чистимо сирі дані від точок для графіку
    df_raw['observation_date'] = pd.to_datetime(df_raw['observation_date'])
    df_raw['price_usd'] = pd.to_numeric(df_raw['price_usd'], errors='coerce')

    df_clean['observation_date'] = pd.to_datetime(df_clean['observation_date'])

    # Створюємо графік
    plt.figure(figsize=(12, 6))

    # Малюємо сирі дані (червоним, пунктиром)
    plt.plot(df_raw['observation_date'], df_raw['price_usd'],
             label='Raw Data (with anomalies)', color='red', alpha=0.3, linestyle='--')

    # Малюємо очищені дані (синім, суцільною лінією)
    plt.plot(df_clean['observation_date'], df_clean['price_cleaned'],
             label='Cleaned Data (Pipeline output)', color='blue', linewidth=1.5)

    plt.title('Henry Hub Natural Gas Price: Raw vs Cleaned')
    plt.xlabel('Date')
    plt.ylabel('Price (USD per MMBtu)')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Зберігаємо результат
    output_path = 'data/processed/price_report.png'
    plt.savefig(output_path)
    print(f"Звіт успішно збережено: {output_path}")

    conn.close()

if __name__ == "__main__":
    generate_report()
