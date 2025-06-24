from flask import Flask, render_template, request
import requests, os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 🔮 DeepSeek API call function
def generate_ai_task(user_goal):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
User's goal: {user_goal}

Generate 1 small, realistic, motivating task the user should do TODAY to move closer to this goal. Be a little funny, a little savage — like a best friend or Indian parent. Language: Hindi if goal is in Hindi, else English.
Return only the task sentence.
"""

    payload = {
        "model": "deepseek-chat",
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": "You are a motivational AI coach with a savage sense of humor."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        res = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=15)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ DeepSeek Error: {e}"

@app.route("/", methods=["GET", "POST"])
def home():
    task = None
    if request.method == "POST":
        user_goal = request.form.get("goal")
        task = generate_ai_task(user_goal)

    return render_template("index.html", task=task)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
