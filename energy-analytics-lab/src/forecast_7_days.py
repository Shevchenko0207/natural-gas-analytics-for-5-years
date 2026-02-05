import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

def train_and_visualize_7day():
    conn = sqlite3.connect('energy_data.db')
    df = pd.read_sql_query("SELECT * FROM gas_prices_ml_7d", conn)
    conn.close()

    df = df.dropna()
    X = df[['current_price', 'lag_1', 'lag_7', 'moving_avg_30', 'month_num']]
    y = df['target_7d']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, shuffle=False)

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    # Отримуємо прогноз на 7 днів від останньої відомої точки
    last_known = X.tail(1)
    prediction_7d = model.predict(last_known)[0]
    current_val = last_known['current_price'].values[0]

    # Підготовка даних для графіка (останні 30 днів + прогноз)
    history = y.tail(30).values
    dates = pd.to_datetime(df['observation_date'].tail(30))

    plt.figure(figsize=(12, 6))

    # Малюємо історію
    plt.plot(range(len(history)), history, label='Historical Price', color='blue', marker='o')

    # Малюємо лінію прогнозу (від останньої точки до прогнозованої через 7 днів)
    plt.plot([len(history)-1, len(history)+6], [current_val, prediction_7d],
             color='red', linestyle='--', marker='s', label='7-Day AI Forecast')

    plt.title(f'Gas Price Forecast: Target ${prediction_7d:.2f}')
    plt.xlabel('Trading Days')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True, alpha=0.3)

    output_path = 'data/processed/forecast_7d.png'
    plt.savefig(output_path)
    print(f"Прогноз на 7 днів збережено: {output_path}")
    print(f"Поточна ціна: ${current_val:.2f} -> Прогноз через 7 днів: ${prediction_7d:.2f}")

if __name__ == "__main__":
    train_and_visualize_7day()
