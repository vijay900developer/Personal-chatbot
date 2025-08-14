import os
import json
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

def get_sales_dataframe():
    sa_json_str = os.environ.get("GOOGLE_SA_JSON")
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    sheet_name = os.environ.get("SHEET_NAME", "Sheet1")

    if not sa_json_str or not sheet_id:
        raise RuntimeError("Missing GOOGLE_SA_JSON or GOOGLE_SHEET_ID env vars.")

    sa_info = json.loads(sa_json_str)
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_info(sa_info, scopes=scopes)
    gc = gspread.authorize(creds)
    ws = gc.open_by_key(sheet_id).worksheet(sheet_name)
    data = ws.get_all_records()  # list of dicts
    df = pd.DataFrame(data)

    # Normalize column names (trim spaces)
    df.columns = [str(c).strip() for c in df.columns]

    return df
