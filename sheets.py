import os
import requests
import pandas as pd
from datetime import datetime

SHEET_WEBAPP_URL = os.environ.get("SHEET_WEBAPP_URL")

def get_sales_dataframe() -> pd.DataFrame:
    """
    Fetch sales data from Google Apps Script WebApp
    """
    try:
        response = requests.get(SHEET_WEBAPP_URL)
        data = response.json()
        df = pd.DataFrame(data)

        # Parse 'Date' column into datetime
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")

        return df
    except Exception as e:
        print("❌ Google Sheet fetch error:", e)
        return pd.DataFrame()

def filter_sales(df: pd.DataFrame, instruction: str) -> str:
    """
    Apply filter and calculate totals.
    """
    if df.empty:
        return "No data available."

    today = datetime.now().date()

    if instruction == "today":
        df = df[df["Date"].dt.date == today]
    elif instruction == "yesterday":
        df = df[df["Date"].dt.date == (today - pd.Timedelta(days=1))]
    elif instruction == "last_month":
        last_month = today.month - 1 if today.month > 1 else 12
        df = df[df["Date"].dt.month == last_month]

    if df.empty:
        return "No sales found for that period."

    total_qty = df["Bill_Qty"].astype(int).sum()
    total_amount = df["Net_Amount"].astype(float).sum()
    return f"✅ Total sales: {total_qty} pcs worth ₹{total_amount:,.0f}"
