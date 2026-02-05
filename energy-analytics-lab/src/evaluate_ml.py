import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

def plot_ml_evaluation():
    conn = sqlite3.connect('energy_data.db')
    df = pd.read_sql_query("SELECT * FROM gas_prices_ml", conn)
    conn.close()

    df = df.dropna()
    X = df[['lag_1', 'lag_7', 'moving_avg_30', 'month_num']]
    y = df['target_price']

    # Розбиваємо так само, як при навчанні
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Отримуємо прогнози для тесту
    predictions = model.predict(X_test)

    # Візуалізація результатів
    plt.figure(figsize=(12, 6))

    # Беремо останні 60 точок для чіткості
    plt.plot(y_test.values[-60:], label='Actual Price', color='#2ecc71', linewidth=2)
    plt.plot(predictions[-60:], label='AI Prediction', color='#e74c3c', linestyle='--', linewidth=2)

    plt.title('Model Evaluation: Actual vs Predicted Gas Prices (Last 60 Days)')
    plt.xlabel('Days (Test Set)')
    plt.ylabel('Price (USD per MMBtu)')
    plt.legend()
    plt.grid(True, alpha=0.3)

    output_path = 'data/processed/ml_evaluation.png'
    plt.savefig(output_path)
    print(f"Графік оцінки моделі збережено: {output_path}")

if __name__ == "__main__":
    plot_ml_evaluation()
