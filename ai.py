import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def ask_ai(prompt: str) -> str:
    """
    Ask AI (OpenAI) to generate a response.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",  # you can switch to gpt-4.1 or gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "You are a helpful assistant for sales queries."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ OpenAI API Error:", e)
        return "Sorry, I could not process that."
