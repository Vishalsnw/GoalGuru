from flask import Flask, render_template, request
import requests, os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
app = Flask(__name__)
API_KEY = os.getenv("DEEPSEEK_API_KEY")

def generate_ai_task(user_goal, lang):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""Date: {today}
Goal: {user_goal}
Lang: {lang}

Give one bold, actionable task (max 2 lines). Desi tone. No repeats."""
    payload = {"model":"deepseek-chat","temperature":0.7,
               "messages":[{"role":"system","content":"You are GoalGuru, a desi tough-love AI."},
                           {"role":"user","content":prompt}]}
    try:
        resp = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        txt = resp.json()["choices"][0]["message"]["content"].strip().replace("**","").strip()
        return txt
    except Exception as e:
        app.logger.error("DeepSeek error: %s", e)
        return "⚠️ Unable to fetch task. Please try again later."

@app.route("/", methods=["GET","POST"])
def home():
    task = None
    if request.method == "POST":
        goal = request.form.get("goal","").strip()
        lang = request.form.get("lang","").strip().lower()
        if goal and lang:
            task = generate_ai_task(goal, lang)
    return render_template("index.html", task=task)

if __name__ == "__main__":
    app.run(debug=True)
