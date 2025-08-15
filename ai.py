import os
import json
from openai import OpenAI
import requests
import pandas as pd
from datetime import datetime, timedelta   # ✅ correct import

SHEET_URL = os.environ["SHEET_WEBAPP_URL"]

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def ask_ai(user_query: str) -> dict:
    prompt = f"""
    You are an assistant for analyzing sales data.
    Extract filters from this query: "{user_query}".
    Possible filters: showroom, product, colour, date range (today, yesterday, last_month, custom).
    Reply ONLY in JSON.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        return json.loads(response.choices[0].message.content)
    except:
        return {"date": "all"}
def calculate_sales_total(period="today"):
    try:
        response = requests.get(SHEET_URL)
        data = response.json()

        today = datetime.today().strftime("%Y-%m-%d")
        total = 0

        if period == "today":
            total = sum(row["Net_Amount"] for row in data if str(row["Date"]) == today)
            return f"✅ Today's total sale is ₹{total}"

        elif period == "yesterday":
            yest = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
            total = sum(row["Net_Amount"] for row in data if str(row["Date"]) == yest)
            return f"✅ Yesterday's total sale was ₹{total}"

        elif period == "last_month":
            this_month = datetime.today().month
            last_month = this_month - 1 if this_month > 1 else 12
            total = sum(row["Net_Amount"] for row in data 
                        if datetime.fromisoformat(row["Date"]).month == last_month)
            return f"✅ Last month’s total sale was ₹{total}"

        else:
            return f"ℹ️ I only support 'today', 'yesterday', and 'last month' right now."

    except Exception as e:
        return f"❌ Error: {e}"

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
