import streamlit as st
import sqlite3
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from pathlib import Path

# Налаштування сторінки
st.set_page_config(page_title="Energy Analytics Lab", layout="wide")

# Шляхи до файлів (виправляємо, щоб вийти з папки src у корінь)
BASE_DIR = Path(__file__).parent.parent  # Додаємо ще один .parent, щоб піднятися вище
MODEL_DIR = BASE_DIR / 'models'
DB_PATH = BASE_DIR / 'energy_data.db'


def load_data():
    """Завантаження даних з БД"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            query = "SELECT * FROM gas_prices_ml_7d ORDER BY observation_date DESC LIMIT 30"
            df = pd.read_sql_query(query, conn)
        return df
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


def prepare_features(row, include_current=False):
    """Підготовка фічів для моделі"""
    features = [
        row['lag_1'],
        row['lag_7'],
        row['moving_avg_30'],
        row['month_num']
    ]
    if include_current:
        features.insert(0, row['current_price'])
    return [features]


def create_forecast_plot(df, last_row, pred_7d):
    """Створення графіку з прогнозом"""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Підготовка даних
    reversed_df = df.iloc[::-1].copy()

    try:
        reversed_df['observation_date'] = pd.to_datetime(reversed_df['observation_date'])
    except Exception as e:
        st.error(f"Date parsing error: {e}")
        return None

    # Історичні дані
    ax.plot(reversed_df['observation_date'], reversed_df['current_price'],
            label='Historical Price', color='#1f77b4', marker='o',
            markersize=4, linewidth=2)

    # Налаштування дат на осі X (виправлено порядок)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=6))  # Спочатку locator
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Потім formatter
    fig.autofmt_xdate(rotation=45, ha='right')  # В кінці - ротація

    # Проекція на 7 днів
    last_date = reversed_df['observation_date'].max()
    future_date = last_date + pd.Timedelta(days=7)

    ax.scatter(future_date, pred_7d, color='red',
               label='AI Target (7 Days)', s=100, zorder=5)
    ax.plot([last_date, future_date],
            [last_row['current_price'], pred_7d],
            color='red', linestyle='--', linewidth=2, alpha=0.7)

    # Оформлення
    ax.set_ylabel("Price (USD per MMBtu)", fontsize=12)
    ax.set_xlabel("Date", fontsize=12)
    ax.legend(fontsize=10, loc='upper left')

    # Ледь помітна сітка (порада користувача)
    ax.grid(True, linestyle=':', alpha=0.5, color='gray')

    # Виділяємо останню відому точку
    ax.scatter(reversed_df['observation_date'].iloc[-1],
               reversed_df['current_price'].iloc[-1],
               color='#1f77b4', s=100, zorder=5,
               edgecolors='white', linewidth=2)

    plt.tight_layout()
    return fig


def main():
    st.title("📊 Natural Gas Price Forecasting Dashboard")
    st.markdown("---")

    # Завантажуємо моделі та дані
    try:
        # Перевірка існування файлів
        if not MODEL_DIR.exists():
            st.error(f"Models directory not found: {MODEL_DIR}")
            return

        if not DB_PATH.exists():
            st.error(f"Database not found: {DB_PATH}")
            return

        # Завантаження моделей
        m1 = joblib.load(MODEL_DIR / 'model_1d.joblib')
        m7 = joblib.load(MODEL_DIR / 'model_7d.joblib')

        # Завантаження даних
        df = load_data()

        if df.empty:
            st.warning("No data available in database!")
            return

        # Останній відомий день
        last_row = df.iloc[0]

        # Метрики
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="Current Market Price",
                value=f"${last_row['current_price']:.2f}"
            )

        # Прогноз на 1 день
        features_1d = prepare_features(last_row, include_current=False)
        pred_1d = m1.predict(features_1d)[0]

        with col2:
            change_1d = ((pred_1d / last_row['current_price']) - 1) * 100
            st.metric(
                label="Next Day Forecast",
                value=f"${pred_1d:.2f}",
                delta=f"{change_1d:.2f}%"
            )

        # Прогноз на 7 днів
        features_7d = prepare_features(last_row, include_current=True)
        pred_7d = m7.predict(features_7d)[0]

        with col3:
            change_7d = ((pred_7d / last_row['current_price']) - 1) * 100
            st.metric(
                label="7-Day Strategic Forecast",
                value=f"${pred_7d:.2f}",
                delta=f"{change_7d:.2f}%"
            )

        st.markdown("---")

        # Візуалізація
        st.subheader("Market Trend and AI Projection")

        fig = create_forecast_plot(df, last_row, pred_7d)

        if fig:
            st.pyplot(fig)
            plt.close(fig)  # Звільняємо пам'ять

        # Додаткова інформація
        with st.expander("📊 View Historical Data"):
            st.dataframe(df.head(10))

        with st.expander("🔍 Model Details"):
            st.write("**Features used:**")
            st.write("- lag_1: Previous day price")
            st.write("- lag_7: Price 7 days ago")
            st.write("- moving_avg_30: 30-day moving average")
            st.write("- month_num: Month number (seasonality)")

    except FileNotFoundError as e:
        st.error(f"File not found: {e}")
        st.info("Check if 'models/' folder and 'energy_data.db' exist in the project directory.")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        import traceback
        st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
