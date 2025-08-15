import os
import requests
from datetime import datetime, timedelta
import pandas as pd

# Load Google Sheet JSON
GOOGLE_SHEET_URL = os.environ["SHEET_WEBAPP_URL"]

def load_sales_data():
    resp = requests.get(GOOGLE_SHEET_URL)
    data = resp.json()
    return pd.DataFrame(data)

def ask_ai(user_query: str) -> str:
    try:
        df = load_sales_data()

        # Convert Date column
        df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")

        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        # Basic query handling (we can later improve with LLM)
        query = user_query.lower()

        if "yesterday" in query:
            filtered = df[df["Date"].dt.date == yesterday]
        elif "today" in query:
            filtered = df[df["Date"].dt.date == today]
        elif "last month" in query:
            last_month = today.month - 1 if today.month > 1 else 12
            filtered = df[df["Date"].dt.month == last_month]
        else:
            filtered = df  # fallback: all data

        total_qty = filtered["Bill_Qty"].astype(int).sum()
        total_amount = filtered["Net_Amount"].astype(float).sum()

        return f"✅ Total sales: {total_qty} pieces worth ₹{total_amount:,.0f}"

    except Exception as e:
        print("AI error:", e)
        return "⚠️ Sorry, I couldn’t fetch sales data right now."
