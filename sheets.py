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

def filter_sales(df: pd.DataFrame, ai_instruction: str) -> str:
    """
    Very simple filter: if AI instruction contains 'today', filter today's date.
    """
    if df.empty:
        return "No data available."

    today = datetime.now().date()

    if "today" in ai_instruction.lower():
        df = df[df["Date"].dt.date == today]
    elif "yesterday" in ai_instruction.lower():
        df = df[df["Date"].dt.date == (today - pd.Timedelta(days=1))]
    # TODO: extend for ranges, months, etc.

    if df.empty:
        return "No sales found for that period."

    total = df["Amount"].sum()
    return f"Total Sales = {total}"
