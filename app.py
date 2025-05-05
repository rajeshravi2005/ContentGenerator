# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from generator import generate_content, supported_models
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import send_file

import time

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Simple user database (in a real app, use a proper database)
users = {
    "admin": {
        "password": generate_password_hash("admin123"),
        "is_pro": True,
        "generation_count": 0,
        "last_generation": 0
    },
    "user": {
        "password": generate_password_hash("user123"),
        "is_pro": False,
        "generation_count": 0,
        "last_generation": 0
    }
}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if username in users and check_password_hash(users[username]["password"], password):
            session["username"] = username
            session["is_pro"] = users[username]["is_pro"]
            return redirect(url_for("home"))
        else:
            error = "Invalid credentials. Please try again."
    
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("is_pro", None)
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if username in users:
            error = "Username already exists. Choose another one."
        else:
            users[username] = {
                "password": generate_password_hash(password),
                "is_pro": False,
                "generation_count": 0,
                "last_generation": 0
            }
            flash("Registration successful! Please login.")
            return redirect(url_for("login"))
    
    return render_template("register.html", error=error)

@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    content = ""
    history = session.get("history", [])
    username = session["username"]
    is_pro = users[username]["is_pro"]
    
    # Rate limiting for free users
    current_time = time.time()
    can_generate = True
    cooldown_remaining = 0
    
    if not is_pro:
        # Check if user has reached daily limit
        if users[username]["generation_count"] >= 5:
            can_generate = False
            error = "You've reached your daily limit of 5 generations. Upgrade to Pro for unlimited access."
            return render_template("index.html", content=content, history=history, 
                                  is_pro=is_pro, error=error, models=supported_models)
        
        # Check cooldown period (60 seconds for free users)
        if current_time - users[username]["last_generation"] < 60:
            cooldown_remaining = 60 - int(current_time - users[username]["last_generation"])
            can_generate = False
            error = f"Please wait {cooldown_remaining} seconds before generating again. Pro users have no cooldown."
            return render_template("index.html", content=content, history=history, 
                                  is_pro=is_pro, error=error, models=supported_models)
    
    if request.method == "POST":
        if not can_generate:
            return redirect(url_for("home"))
        
        topic = request.form["topic"]
        word_count = int(request.form.get("word_count", 500))
        model = request.form.get("model", "mistralai/mistral-small-3.1-24b-instruct:free")
        tone = request.form.get("tone", "informative")
        
        # Word count limits for free users
        if not is_pro and word_count > 800:
            word_count = 800
            flash("Free users are limited to 800 words. Upgrade to Pro for up to 2000 words.")
        
        # Update user statistics
        users[username]["generation_count"] += 1
        users[username]["last_generation"] = current_time
        
        try:
            content = generate_content(topic, word_count, model, tone)
            
            # Save to history (limit history size)
            history.insert(0, {"topic": topic, "preview": content[:100] + "..."})
            if len(history) > 10:
                history = history[:10]
            session["history"] = history
            
            # Save generated content to file
            filename = f"generated_{int(time.time())}.txt"
            filepath = os.path.join("generated_content", filename)
            os.makedirs("generated_content", exist_ok=True)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Topic: {topic}\n")
                f.write(f"Word Count Target: {word_count}\n")
                f.write(f"Model: {model}\n")
                f.write(f"Tone: {tone}\n\n")
                f.write(content)
            
            session["last_generated"] = filepath
        except Exception as e:
            flash(f"Error generating content: {str(e)}")
    
    return render_template("index.html", content=content, history=history, 
                          is_pro=is_pro, models=supported_models)

@app.route("/upgrade")
@login_required
def upgrade():
    return render_template("upgrade.html")

@app.route("/process_upgrade", methods=["POST"])
@login_required
def process_upgrade():
    # In a real app, process payment here
    username = session["username"]
    users[username]["is_pro"] = True
    session["is_pro"] = True
    flash("Congratulations! You're now a Pro user with premium features.")
    return redirect(url_for("home"))

@app.route("/download")
@login_required
def download():
    if "last_generated" in session:
        return send_file(session["last_generated"], as_attachment=True)
    flash("No content to download. Generate content first.")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)