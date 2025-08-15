import os
import json
import requests
from flask import Flask, request, jsonify
from ai import ask_ai, calculate_sales_total
from sheets import get_sales_dataframe, filter_sales

app = Flask(__name__)

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN")

# ✅ Root
@app.route("/", methods=["GET"])
def home():
    return "✅ WhatsApp Sales Bot is running!"

# ✅ Webhook Verification (for Meta)
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

# ✅ Handle Incoming Messages
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("📩 Incoming:", data)

        # Navigate to value
        changes = data.get("entry", [])[0].get("changes", [])[0]
        value = changes.get("value", {})

        # Check if it's a message event
        if "messages" in value:
            message = value["messages"][0]
            user_number = message["from"]
            user_text = message["text"]["body"].lower()

            print(f"✅ User {user_number} said: {user_text}")

            # 🔹 Get filters using AI
            filters = ask_ai(user_text)

            # 🔹 Apply filters on Google Sheet
            df = get_sales_dataframe()
            filtered = filter_sales(df, filters)
            reply = calculate_sales_total(filtered)

            send_whatsapp_message(user_number, reply)

    except Exception as e:
        print("❌ Webhook error:", str(e))

    return "ok", 200



def send_whatsapp_message(to_number, text):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    response = requests.post(url, headers=headers, json=payload)
    print("✅ WhatsApp response:", response.text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
