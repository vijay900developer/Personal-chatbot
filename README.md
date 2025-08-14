# WhatsApp + Google Sheets Personal Analytics Chatbot

A minimal, production-ready Flask app that:
- Receives WhatsApp messages via the Meta WhatsApp Cloud API
- Uses a **tiny LLM pass** to parse user intent/filters into strict JSON (to save tokens)
- Pulls data from **Google Sheets** (via Service Account) into **pandas**
- Applies all **filters & calculations in Python** (token efficient)
- Replies back to the user on WhatsApp
- Deploys cleanly on **Render** with `render.yaml`

> Timezone defaults to `Asia/Kolkata` (change via `TZ` env if needed).

## Architecture

```
app.py
├─ ai.py          -> Extracts structured filters from user text with small LLM (JSON only)
├─ sheets.py      -> Connects to Google Sheets using a Service Account; returns pandas DataFrame
├─ calc.py        -> Applies filters (date ranges, outlets, products, etc.) and computes metrics
└─ whatsapp.py    -> Sends WhatsApp messages via Cloud API
```

## Expected Google Sheet schema

**Required columns (case-sensitive):**
- `Date` (e.g., `2025-08-12` or `12/08/2025`)
- `Amount` (numeric)
- Optional filters: `Outlet`, `Product`, `Salesperson`, `Customer`, etc.

Use your own column names, but keep them consistent. You can update mapping in `calc.py` if needed.

## Environment Variables

Set these in Render (or locally in `.env` for testing):

- `OPENAI_API_KEY` — your OpenAI API key
- `VERIFY_TOKEN` — webhook verification token (any secret string you set in Meta webhook setup)
- `WHATSAPP_TOKEN` — WhatsApp Cloud API Permanent Access Token
- `WHATSAPP_PHONE_NUMBER_ID` — Cloud API Phone Number ID
- `GOOGLE_SA_JSON` — the **entire** Service Account JSON contents (paste as a single line)
- `GOOGLE_SHEET_ID` — your Google Sheet ID (from the URL)
- `SHEET_NAME` — the tab name (default: `Sheet1`)
- `TZ` — timezone string (default: `Asia/Kolkata`)

### Service Account Setup (Google Sheets)
1. Create a Service Account in Google Cloud -> Enable Google Sheets API + Google Drive API.
2. Create a JSON key. Copy the **entire contents** into `GOOGLE_SA_JSON` env var.
3. Share your Google Sheet with the Service Account email (Viewer is sufficient).

## Local run (optional)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export FLASK_ENV=development
export PORT=5000
python app.py
```
Use something like `ngrok http 5000` for a temporary public URL to set the webhook in Meta Dev Console.

## Deploy on Render

1. Push this folder to a GitHub repo.
2. In Render:
   - **New Web Service** -> Connect your repo
   - Runtime: Python 3.11+
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`
   - Add all Environment Variables above
3. Alternatively, **Blueprint** deploy with the provided `render.yaml`.

## Example queries
- "What is total sale today?"
- "Yesterday sales for Indore?"
- "Total last month for Sherwani in Bhopal"
- "Sum amount between 1 Aug and 10 Aug for Outlet Indore"

## Notes on token efficiency
- Only `ai.extract_filters()` uses the model with a tightly-scoped system prompt to return compact JSON.
- All filtering, grouping, date parsing, and aggregation uses **pandas** in `calc.py`.
