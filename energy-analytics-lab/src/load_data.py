import sqlite3
import csv

def load_csv_to_sql():
    db_path = 'energy_data.db'
    csv_path = 'data/raw/DHHNGSP.csv' # Переконайтеся, що назва файлу збігається

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        with open(csv_path, 'r') as f:
            # Читаємо CSV, автоматично розділяючи за комою
            reader = csv.reader(f)
            next(reader)  # Пропускаємо заголовок (observation_date,DHHNGSP)

            # Завантажуємо дані
            cursor.executemany(
                "INSERT OR IGNORE INTO gas_prices_raw (observation_date, price_usd) VALUES (?, ?)",
                reader
            )

        conn.commit()
        print(f"Дані успішно завантажені! Додано рядків: {cursor.rowcount}")

    except Exception as e:
        print(f"Помилка завантаження: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    load_csv_to_sql()
