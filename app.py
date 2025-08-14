import os
import json
import logging
from flask import Flask, request, jsonify
from datetime import datetime
import pytz

from ai import extract_filters
from sheets import get_sales_dataframe
from calc import run_query
from whatsapp import send_whatsapp_text

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.INFO)

TZ = os.getenv("TZ", "Asia/Kolkata")
IST = pytz.timezone(TZ)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

@app.get("/")
def health():
    return {"ok": True, "time": datetime.now(IST).isoformat()}

# WhatsApp webhook verification
@app.get("/webhook")
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

# WhatsApp webhook receiver
@app.post("/webhook")
def incoming():
    data = request.get_json(force=True, silent=True) or {}
    try:
        entries = data.get("entry", [])
        for entry in entries:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                if not messages:
                    continue
                for msg in messages:
                    msg_type = msg.get("type")
                    from_wa = msg.get("from")
                    text = None
                    if msg_type == "text":
                        text = msg["text"]["body"]
                    elif msg_type == "interactive":
                        # Support button/list replies
                        interactive = msg.get("interactive", {})
                        if interactive.get("type") == "button_reply":
                            text = interactive["button_reply"].get("title")
                        elif interactive.get("type") == "list_reply":
                            text = interactive["list_reply"].get("title")
                    else:
                        text = None

                    if not text:
                        send_whatsapp_text(f"Hi! Please send a text question like 'total sale today'.", from_wa)
                        continue

                    # 1) Get sheet data (cached per request in this simple version)
                    df = get_sales_dataframe()

                    # 2) Low-token LLM to parse filters & metric
                    intent = extract_filters(text)

                    # 3) Execute calc in Python
                    result_lines = run_query(df, intent)

                    # 4) Respond back
                    reply = "\n".join(result_lines)
                    send_whatsapp_text(reply, from_wa)
        return "OK", 200
    except Exception as e:
        logging.exception("Webhook handling error")
        return "Internal Server Error", 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
