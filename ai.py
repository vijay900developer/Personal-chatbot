import os 
import requests 
from datetime 
import datetime, timedelta 
import pandas as pd

# Load Google Sheet JSON 
GOOGLE_SHEET_URL = os.environ["SHEET_WEBAPP_URL"]

def load_sales_data(): 
    resp = requests.get(GOOGLE_SHEET_URL) 
    data = resp.json() 
    return pd.DataFrame(data)

def ask_ai(user_query: str) -> str:
    """
    Interpret user query and return filter instructions.
    """
    query = user_query.lower()
    today = datetime.now().date()

    if "yesterday" in query:
        return "yesterday"
    elif "today" in query:
        return "today"
    elif "last month" in query:
        return "last_month"
    else:
        return "all"

    total_qty = filtered["Bill_Qty"].astype(int).sum() 
    total_amount = filtered["Net_Amount"].astype(float).sum()
    return f"✅ Total sales: {total_qty} pieces worth ₹{total_amount:,.0f}"

    except Exception as e: 
       print("AI error:", e) 
       return "⚠️ Sorry, I couldn’t fetch sales data right now."
