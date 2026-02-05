import sqlite3
import pandas as pd

def clean_energy_data():
    db_path = 'energy_data.db'
    conn = sqlite3.connect(db_path)

    # 1. Завантажуємо дані з SQL в Pandas DataFrame
    df = pd.read_sql_query("SELECT * FROM gas_prices_cleaned", conn)

    # 2. Обробка пропусків: заповнюємо NaN значенням попереднього дня
    # Це важливо для ML, щоб не було розривів у графіку
    df['price_cleaned'] = df['price_cleaned'].ffill()

    # 3. Зберігаємо очищені дані в нову таблицю або CSV
    df.to_sql('gas_prices_final', conn, if_exists='replace', index=False)
    df.to_csv('data/processed/gas_prices_clean.csv', index=False)

    print(f"Очищення завершено. Файл збережено в data/processed/gas_prices_clean.csv")
    conn.close()

if __name__ == "__main__":
    clean_energy_data()
