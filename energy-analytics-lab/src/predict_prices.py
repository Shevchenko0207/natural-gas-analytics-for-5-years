import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

def train_prediction_model():
    conn = sqlite3.connect('energy_data.db')

    # 1. Завантажуємо підготовлені ознаки
    df = pd.read_sql_query("SELECT * FROM gas_prices_ml", conn)
    conn.close()

    # Видаляємо рядки з порожніми лагами (перші кілька днів)
    df = df.dropna()

    # Визначаємо X (фактори) та y (ціль)
    X = df[['lag_1', 'lag_7', 'moving_avg_30', 'month_num']]
    y = df['target_price']

    # 2. Розбиваємо на навчальну та тестову вибірки (80% на 20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # 3. Навчаємо модель
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 4. Оцінюємо точність
    predictions = model.predict(X_test)
    error = mean_absolute_error(y_test, predictions)

    print(f"--- РЕЗУЛЬТАТИ НАВЧАННЯ ШІ ---")
    print(f"Середня помилка прогнозу: ${error:.2f}")

    # Останній прогноз (на завтра)
    last_data = X.tail(1)
    next_day_pred = model.predict(last_data)
    print(f"Прогноз ціни на наступний торговий день: ${next_day_pred[0]:.2f}")

if __name__ == "__main__":
    train_prediction_model()
