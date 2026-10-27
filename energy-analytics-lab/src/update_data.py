import os
import sqlite3

import pandas as pd

# Configuration
API_KEY = os.getenv('FRED_API_KEY')
DB_PATH = os.path.join(os.path.dirname(__file__), '../energy_data.db')
TABLE = 'gas_prices_ml_7d'  # саме цю таблицю читає app.py
CHECK_ROWS = 15             # скільки останніх рядків звіряємо перед записом
TOL = 1e-3
CHECK_COLS = ['current_price', 'lag_1', 'lag_7', 'moving_avg_30', 'target_7d']


def build_features(prices, window_includes_current):
    """Рахує ті самі фічі, що лежать у таблиці gas_prices_ml_7d."""
    s = prices.sort_index()
    if window_includes_current:
        ma30 = s.rolling(30).mean()
    else:
        ma30 = s.shift(1).rolling(30).mean()
    df = pd.DataFrame({
        'observation_date': s.index.strftime('%Y-%m-%d'),
        'target_7d': s.shift(-7).values,
        'current_price': s.values,
        'lag_1': s.shift(1).values,
        'lag_7': s.shift(7).values,
        'moving_avg_30': ma30.values,
        'month_num': s.index.strftime('%m'),
    })
    return df.set_index('observation_date', drop=False)


def check_match(stored, feats):
    """Порівнює збережені рядки з перерахованими. Повертає (ok, опис розбіжності)."""
    for _, row in stored.iterrows():
        key = str(row['observation_date'])[:10]
        if key not in feats.index:
            return False, f"{key}: немає в даних FRED"
        for col in CHECK_COLS:
            sv = row[col]
            if pd.isna(sv):
                continue
            fv = feats.at[key, col]
            if pd.isna(fv) or abs(float(sv) - float(fv)) > TOL:
                return False, f"{key} {col}: в базі={sv}, пораховано={fv}"
    return True, ""


def pick_convention(conn, prices):
    """Підбирає спосіб розрахунку moving_avg_30, що збігається з існуючими даними."""
    stored = pd.read_sql_query(
        f"SELECT * FROM {TABLE} ORDER BY observation_date DESC LIMIT {CHECK_ROWS}", conn)
    if stored.empty:
        raise SystemExit(f"Таблиця {TABLE} порожня, нема з чим звірити розрахунок")
    problems = []
    for includes in (True, False):
        ok, msg = check_match(stored, build_features(prices, includes))
        if ok:
            return includes
        problems.append(f"window_includes_current={includes}: {msg}")
    raise SystemExit(
        "Фічі не збігаються з тим, що вже є в базі. Дані НЕ записано.\n" + "\n".join(problems))


def run(prices, conn):
    includes = pick_convention(conn, prices)
    feats = build_features(prices, includes)

    last = conn.execute(f"SELECT MAX(observation_date) FROM {TABLE}").fetchone()[0]
    last = str(last)[:10]

    new = feats[feats['observation_date'] > last].dropna(
        subset=['current_price', 'lag_1', 'lag_7', 'moving_avg_30'])
    rows = [
        (r.observation_date,
         None if pd.isna(r.target_7d) else float(r.target_7d),
         float(r.current_price), float(r.lag_1), float(r.lag_7),
         float(r.moving_avg_30), r.month_num)
        for r in new.itertuples()
    ]
    if rows:
        conn.executemany(
            f"INSERT INTO {TABLE} (observation_date, target_7d, current_price, "
            f"lag_1, lag_7, moving_avg_30, month_num) VALUES (?,?,?,?,?,?,?)", rows)
    print(f"Додано рядків: {len(rows)}")

    # target_7d стає відомим лише через 7 торгових днів, тому дозаповнюємо
    filled = 0
    pending = conn.execute(f"SELECT observation_date FROM {TABLE} WHERE target_7d IS NULL").fetchall()
    for (d,) in pending:
        key = str(d)[:10]
        if key in feats.index and pd.notna(feats.at[key, 'target_7d']):
            conn.execute(f"UPDATE {TABLE} SET target_7d = ? WHERE observation_date = ?",
                         (float(feats.at[key, 'target_7d']), d))
            filled += 1
    print(f"Дозаповнено target_7d: {filled}")
    conn.commit()

    print("\nОстанні рядки:")
    for r in conn.execute(
            f"SELECT observation_date, current_price FROM {TABLE} "
            f"ORDER BY observation_date DESC LIMIT 5"):
        print(f"  {r[0]}: ${r[1]:.2f}")


def update_gas_prices():
    if not API_KEY:
        raise ValueError("FRED_API_KEY environment variable not set!")
    from fredapi import Fred
    print("Fetching data from FRED API...")
    prices = Fred(api_key=API_KEY).get_series('DHHNGSP').dropna()
    with sqlite3.connect(DB_PATH) as conn:
        run(prices, conn)


if __name__ == "__main__":
    update_gas_prices()
