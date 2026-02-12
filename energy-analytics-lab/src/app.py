import streamlit as st
import sqlite3
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from pathlib import Path
import os

# 1. НАЛАШТУВАННЯ ШЛЯХІВ
CURRENT_DIR = Path(__file__).parent.resolve()

# Оскільки app.py в папці src, а база поруч із папкою src
DB_PATH = CURRENT_DIR.parent / 'energy_data.db'
MODEL_DIR = CURRENT_DIR.parent / 'models'

st.set_page_config(page_title="Energy Analytics Lab", layout="wide")

def load_data():
    """Завантаження даних з БД з перевіркою шляху"""
    try:
        if not DB_PATH.exists():
            st.error(f"Базу даних не знайдено за шляхом: {DB_PATH}")
            return pd.DataFrame()
            
        with sqlite3.connect(DB_PATH) as conn:
            # Беремо останні 30 записів для графіка
            query = "SELECT * FROM gas_prices_ml_7d ORDER BY observation_date DESC LIMIT 30"
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Помилка бази даних: {e}")
        return pd.DataFrame()

def prepare_features(row, include_current=False):
    """Підготовка фічів для ML моделей"""
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
    """Створення професійного графіку"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Створюємо копію та конвертуємо дати
    plot_df = df.copy()
    plot_df['observation_date'] = pd.to_datetime(plot_df['observation_date'])
    plot_df = plot_df.sort_values('observation_date')

    # Історична лінія
    ax.plot(plot_df['observation_date'], plot_df['current_price'], 
            label='Історична ціна', color='#1f77b4', marker='o', 
            markersize=4, linewidth=2)

    # Налаштування осей
    ax.xaxis.set_major_locator(MaxNLocator(nbins=8))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate(rotation=45)

    # Прогноз (червона точка)
    last_date = plot_df['observation_date'].max()
    future_date = last_date + pd.Timedelta(days=7)
    
    ax.scatter(future_date, pred_7d, color='red', label='AI Прогноз (7 днів)', s=100, zorder=5)
    ax.plot([last_date, future_date], [last_row['current_price'], pred_7d], 
            color='red', linestyle='--', linewidth=2, alpha=0.6)

    # Оформлення
    ax.set_ylabel("USD per MMBtu", fontsize=10)
    ax.set_title(f"Тренд цін та прогноз (Останнє оновлення: {last_date.date()})", fontsize=14)
    ax.legend()
    ax.grid(True, linestyle=':', alpha=0.4)
    
    plt.tight_layout()
    return fig

def main():
    st.title("📊 Natural Gas Analytics & Prediction")
    st.markdown(f"**Статус системи:** Автоматичне оновлення через GitHub Actions ✅")

    try:
        # Завантажуємо моделі
        m1 = joblib.load(MODEL_DIR / 'model_1d.joblib')
        m7 = joblib.load(MODEL_DIR / 'model_7d.joblib')

        # Завантажуємо дані
        df = load_data()
        if df.empty:
            return

        last_row = df.iloc[0] # Остання ціна (бо ORDER BY DESC)

        # Ряд метрик
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Поточна ціна (FRED)", f"${last_row['current_price']:.2f}", 
                      help=f"Дата: {last_row['observation_date']}")
        with c2:
            feat1 = prepare_features(last_row, False)
            p1 = m1.predict(feat1)[0]
            diff1 = ((p1/last_row['current_price'])-1)*100
            st.metric("Прогноз на завтра", f"${p1:.2f}", f"{diff1:.2f}%")
        with c3:
            feat7 = prepare_features(last_row, True)
            p7 = m7.predict(feat7)[0]
            diff7 = ((p7/last_row['current_price'])-1)*100
            st.metric("Прогноз на 7 днів", f"${p7:.2f}", f"{diff7:.2f}%")

        # Графік
        st.pyplot(create_forecast_plot(df, last_row, p7))

        # Таблиця
        with st.expander("Переглянути сирі дані (останні 10 записів)"):
            st.write(df.head(10))

    except Exception as e:
        st.error(f"Помилка запуску: {e}")
        st.info("Переконайтеся, що папка 'models' та файл 'energy_data.db' знаходяться в 'energy-analytics-lab/'")

if __name__ == "__main__":
    main()
