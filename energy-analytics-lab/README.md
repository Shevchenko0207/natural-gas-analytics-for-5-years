# 📊 Natural Gas Price Forecasting Dashboard
# 🚀 Live Demo: [natural-gas-analytics-for-5-years.onrender.com](https://natural-gas-analytics-for-5-years.onrender.com/)

An end-to-end Machine Learning application that predicts Natural Gas prices for **1-day** and **7-day** horizons. This project features a professional dashboard built with **Streamlit** and a predictive engine powered by **Scikit-learn**.

## 🚀 Live Features
* **Real-time Metrics**: Displays current market prices and AI-calculated forecasts.
* **Smart Visualization**: Interactive time-series charts showing historical trends vs. future projections.
* **Machine Learning**: Uses dual models (Random Forest/Linear Regression) trained on historical lags and seasonal features.
* **Clean UI**: Professional English interface with automated date formatting to ensure readability.

## 🛠️ Tech Stack
* **Language**: Python 3.x
* **Dashboard**: Streamlit
* **ML Libraries**: Scikit-learn, Joblib, Pandas
* **Database**: SQLite3
* **Plotting**: Matplotlib

## 📂 Project Structure
* `src/app.py`: The main dashboard application.
* `models/`: Pre-trained AI models (`.joblib` files).
* `energy_data.db`: Local SQLite database containing price history.
* `requirements.txt`: List of necessary Python libraries for deployment.

## ⚙️ Installation & Local Run
1. **Clone the repository**:
   ```bash
   git clone <your-repository-link>
   cd energy-analytics-lab
2.	Install dependencies:
Bash
pip install -r requirements.txt
3.	Launch the Dashboard:
Bash
streamlit run src/app.py
🌐 Deployment
This project is configured for easy deployment on Render or Streamlit Community Cloud.
The BASE_DIR logic in app.py ensures that paths are handled correctly across different server environments.

