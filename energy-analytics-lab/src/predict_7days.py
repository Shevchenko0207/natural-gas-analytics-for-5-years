import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

def train_7day_model():
    conn = sqlite3.connect('energy_data.db')

    # Завантажуємо нову таблицю
    df = pd.read_sql_query("SELECT * FROM gas_prices_ml_7d", conn)
    conn.close()

    df = df.dropna()

    # Вибираємо фактори впливу
    X = df[['current_price', 'lag_1', 'lag_7', 'moving_avg_30', 'month_num']]
    y = df['target_7d']

    # Хронологічний поділ (важливо для часових рядів)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, shuffle=False)

    # Навчаємо модель з більшою кількістю дерев для кращої стабільності
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    # Оцінка
    predictions = model.predict(X_test)
    error = mean_absolute_error(y_test, predictions)

    print(f"--- АНАЛІЗ ПРОГНОЗУ НА 7 ДНІВ ---")
    print(f"Середня помилка (MAE): ${error:.2f}")

    # Прогноз на майбутнє
    # Беремо поточні дані (останній відомий день)
    last_known_data = X.tail(1)
    prediction_7d = model.predict(last_known_data)

    print(f"Очікувана ціна через 7 торгових днів: ${prediction_7d[0]:.2f}")

    if prediction_7d[0] > last_known_data['current_price'].values[0]:
        print("Порада: Очікується РІСТ ціни. Можливе зростання витрат.")
    else:
        print("Порада: Очікується ПАДІННЯ ціни. Сприятливий час для закупівлі.")

if __name__ == "__main__":
    train_7day_model()
