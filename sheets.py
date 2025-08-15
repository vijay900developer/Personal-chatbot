import os
import requests
import pandas as pd

SHEET_WEBAPP_URL = os.environ.get("SHEET_WEBAPP_URL")

def get_sales_dataframe():
    if not SHEET_WEBAPP_URL:
        raise RuntimeError("Missing SHEET_WEBAPP_URL environment variable")

    response = requests.get(SHEET_WEBAPP_URL)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data)

    # Clean column names
    df.columns = [str(c).strip() for c in df.columns]

    # Convert "Date" column
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")

    # Convert Amount to numeric
    if "Amount" in df.columns:
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    return df


def filter_sales(df, filter_info):
    """
    filter_info example:
    {
        "type": "date_range",
        "start": "2025-08-01",
        "end": "2025-08-12"
    }
    """
    if df.empty or "Amount" not in df.columns:
        return 0

    if filter_info.get("type") == "date_range":
        start = pd.to_datetime(filter_info["start"])
        end = pd.to_datetime(filter_info["end"])
        df_filtered = df[(df["Date"] >= start) & (df["Date"] <= end)]
        return df_filtered["Amount"].sum()

    elif filter_info.get("type") == "today":
        today = pd.Timestamp.now().normalize()
        df_filtered = df[df["Date"] == today]
        return df_filtered["Amount"].sum()

    elif filter_info.get("type") == "yesterday":
        yesterday = (pd.Timestamp.now() - pd.Timedelta(days=1)).normalize()
        df_filtered = df[df["Date"] == yesterday]
        return df_filtered["Amount"].sum()

    elif filter_info.get("type") == "month":
        month = filter_info["month"]
        year = filter_info["year"]
        df_filtered = df[(df["Date"].dt.month == month) & (df["Date"].dt.year == year)]
        return df_filtered["Amount"].sum()

    return 0
