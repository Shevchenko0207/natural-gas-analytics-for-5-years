import sqlite3
import sys

def execute_sql(sql_file):
    conn = sqlite3.connect('energy_data.db')
    cursor = conn.cursor()
    try:
        with open(sql_file, 'r') as f:
            cursor.executescript(f.read())
        conn.commit()
        print(f"Успішно виконано: {sql_file}")
    except Exception as e:
        print(f"Помилка у {sql_file}: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Беремо назву файлу з команди в терміналі
    file_to_run = sys.argv[1] if len(sys.argv) > 1 else 'sql/extract_data.sql'
    execute_sql(file_to_run)
