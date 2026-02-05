import pandas as pd
import sqlite3
import os
from fredapi import Fred
from datetime import datetime

# Configuration
API_KEY = os.getenv('FRED_API_KEY')
DB_PATH = os.path.join(os.path.dirname(__file__), '../energy_data.db')

def init_database():
    """Create database and table if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gas_prices (
            date TEXT PRIMARY KEY,
            price REAL NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized")

def update_gas_prices():
    """Fetch latest gas prices from FRED and update database"""
    
    # Check if API key exists
    if not API_KEY:
        raise ValueError("FRED_API_KEY environment variable not set!")
    
    # Initialize database
    init_database()
    
    try:
        # Connect to FRED API
        fred = Fred(api_key=API_KEY)
        
        # Get Henry Hub Natural Gas Spot Price (Daily)
        print("Fetching data from FRED API...")
        data = fred.get_series('DHHNGSP')
        
        if data.empty:
            print("No data returned from FRED API")
            return
        
        # Get the latest non-null value
        data = data.dropna()
        latest_date = data.index[-1]
        latest_price = data.iloc[-1]
        
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if this date already exists
        date_str = latest_date.strftime('%Y-%m-%d')
        cursor.execute("SELECT price FROM gas_prices WHERE date = ?", (date_str,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"Data for {date_str} already exists (${existing[0]:.2f})")
            # Update if price changed
            if abs(existing[0] - latest_price) > 0.001:
                cursor.execute(
                    "UPDATE gas_prices SET price = ?, updated_at = CURRENT_TIMESTAMP WHERE date = ?",
                    (latest_price, date_str)
                )
                conn.commit()
                print(f"Updated: {date_str} - ${latest_price:.2f} (changed from ${existing[0]:.2f})")
            else:
                print("No price change, skipping update")
        else:
            # Insert new record
            cursor.execute(
                "INSERT INTO gas_prices (date, price) VALUES (?, ?)",
                (date_str, latest_price)
            )
            conn.commit()
            print(f"Inserted: {date_str} - ${latest_price:.2f}")
        
        # Show recent entries
        cursor.execute("SELECT date, price FROM gas_prices ORDER BY date DESC LIMIT 5")
        recent = cursor.fetchall()
        print("\nRecent entries:")
        for row in recent:
            print(f"  {row[0]}: ${row[1]:.2f}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error updating gas prices: {e}")
        raise

if __name__ == "__main__":
    update_gas_prices()
