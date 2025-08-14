import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a strict JSON generator to parse sales analytics questions.
Only output valid JSON. No extra text.
Return keys:
- operation: one of ["sum","avg","count"]
- metric: choose a numeric column name to aggregate, default "Amount" if not given
- timeframe:
    { "type": "today" | "yesterday" | "this_month" | "last_month" |
      "last_7_days" | "date_range",
      "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" (only when type="date_range") }
- filters: object where keys are sheet column names, values are exact strings to match (case-insensitive)
- group_by: optional array of column names (e.g., ["Outlet"])
- top_k: optional integer (return top K groups by metric)
If user asks plain total without metric, use operation="sum" and metric="Amount".
"""

def extract_filters(user_text: str) -> dict:
    """Call a small model to convert free-form text to strict JSON for filtering."""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=200,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            response_format={"type": "json_object"}
        )
        raw = resp.choices[0].message.content
        data = json.loads(raw)
        # minimal normalization
        if "operation" not in data:
            data["operation"] = "sum"
        if "metric" not in data:
            data["metric"] = "Amount"
        if "timeframe" not in data:
            data["timeframe"] = {"type": "today"}
        if "filters" not in data:
            data["filters"] = {}
        return data
    except Exception:
        # Fallback: basic default if model fails (keeps bot functional)
        return {
            "operation": "sum",
            "metric": "Amount",
            "timeframe": {"type": "today"},
            "filters": {}
        }
