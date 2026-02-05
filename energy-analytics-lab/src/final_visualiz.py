import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

def generate_final_report():
    conn = sqlite3.connect('energy_data.db')

    # 1. Завантажуємо дані з нашої SQL-таблиці з метриками
    query = "SELECT observation_date, price_cleaned, moving_avg_30 FROM gas_prices_metrics"
    df = pd.read_sql_query(query, conn)

    # Також завантажимо сирі дані для фонового порівняння
    df_raw = pd.read_sql_query("SELECT observation_date, price_usd FROM gas_prices_raw", conn)

    # Конвертація типів
    df['observation_date'] = pd.to_datetime(df['observation_date'])
    df_raw['observation_date'] = pd.to_datetime(df_raw['observation_date'])
    df_raw['price_usd'] = pd.to_numeric(df_raw['price_usd'], errors='coerce')

    # 2. Побудова графіку
    plt.figure(figsize=(14, 7))

    # Сирі дані (блідо-червоний фон для аномалій)
    plt.plot(df_raw['observation_date'], df_raw['price_usd'],
             label='Raw Price (Anomalies)', color='red', alpha=0.15, linestyle=':')

    # Очищені дані (основна ціна)
    plt.plot(df['observation_date'], df['price_cleaned'],
             label='Cleaned Price', color='dodgerblue', alpha=0.6)

    # 30-денне ковзне середнє (жирна лінія тренду)
    plt.plot(df['observation_date'], df['moving_avg_30'],
             label='30-Day Trend (Moving Avg)', color='navy', linewidth=2)

    # Оформлення
    plt.title('Henry Hub Gas Price Analysis: Market Trend vs Volatility', fontsize=14)
    plt.xlabel('Year')
    plt.ylabel('Price (USD per MMBtu)')
    plt.legend(loc='upper left')
    plt.grid(True, which='both', linestyle='--', alpha=0.5)

    # Збереження
    output_path = 'data/processed/final_market_analysis.png'
    plt.savefig(output_path, dpi=300) # Висока якість для звіту
    print(f"Фінальний звіт збережено: {output_path}")

    conn.close()

if __name__ == "__main__":
    generate_report_exists = True # Валідація кроку
    generate_final_report()
