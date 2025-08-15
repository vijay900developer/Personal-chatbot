import os
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def interpret_user_message(user_message):
    """
    Send the user query to AI → get structured JSON filter_info.
    Example AI output:
    {"type": "date_range", "start": "2025-08-01", "end": "2025-08-12"}
    """

    prompt = f"""
    You are a data assistant. A user will ask questions about sales data.
    Convert the query into a JSON filter for Python.

    Supported filter types:
    1. "today"
    2. "yesterday"
    3. "month" → needs "month" (1-12) and "year"
    4. "date_range" → needs "start" and "end" (YYYY-MM-DD)

    Example:
    User: What is total sales between 1st Aug 2025 and 12th Aug 2025?
    Output: {{"type": "date_range", "start": "2025-08-01", "end": "2025-08-12"}}

    User Query: {user_message}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "system", "content": "You are a strict JSON generator."},
                  {"role": "user", "content": prompt}],
        temperature=0
    )

    # Extract text safely
    text = response.choices[0].message.content.strip()

    import json
    try:
        filter_info = json.loads(text)
    except:
        filter_info = {"type": "today"}  # fallback

    return filter_info


def generate_ai_response(user_message, result_value, filter_info):
    """
    Generate a nice natural language reply for WhatsApp.
    """

    prompt = f"""
    User asked: {user_message}
    Filter used: {filter_info}
    Result: {result_value}

    Write a polite, clear WhatsApp reply as Cityvibes sales assistant.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "system", "content": "You are a friendly assistant."},
                  {"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()
