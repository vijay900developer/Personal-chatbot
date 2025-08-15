from flask import Flask, request, jsonify
import os
from sheet_utils import get_sales_dataframe, filter_sales
from ai_utils import interpret_user_message, generate_ai_response

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "✅ Personal Chatbot is running!"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "")

        # Step 1: Ask AI to interpret user request (date range, filter type, etc.)
        filter_info = interpret_user_message(user_message)

        # Step 2: Load sales data from Google Sheet JSON WebApp
        df = get_sales_dataframe()

        # Step 3: Apply filter in Python based on AI interpretation
        result_value = filter_sales(df, filter_info)

        # Step 4: Generate AI-friendly reply
        reply = generate_ai_response(user_message, result_value, filter_info)

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
