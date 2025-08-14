import os
import requests
import pandas as pd

def get_sales_dataframe():
    """
    Fetch sales data from a published Google Apps Script Web App URL
    that returns JSON (array of objects).
    """
    web_app_url = os.environ.get("SHEET_WEBHOOK_URL")

    if not web_app_url:
        raise RuntimeError("Missing GOOGLE_SHEET_WEBAPP_URL env var.")

    # Call the web app
    resp = requests.get(web_app_url)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch data from web app: {resp.status_code} {resp.text}")

    data = resp.json()  # Expecting list of dicts
    df = pd.DataFrame(data)

    # Normalize column names
    df.columns = [str(c).strip() for c in df.columns]

    return df
