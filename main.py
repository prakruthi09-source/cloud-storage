from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
import json

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"
USER_DB = "users.json"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(USER_DB):
    with open(USER_DB, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USER_DB, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f)

@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    username = session["user"]
    user_folder = os.path.join(UPLOAD_FOLDER, username)
    os.makedirs(user_folder, exist_ok=True)
    files = os.listdir(user_folder)
    return render_template("index.html", files=files)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = load_users()
        if username in users:
            return render_template("register.html", error="Username already exists")
        users[username] = password
        save_users(users)
        os.makedirs(os.path.join(UPLOAD_FOLDER, username), exist_ok=True)
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = load_users()
        if username in users and users[username] == password:
            session["user"] = username
            return redirect("/")
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

@app.route("/upload", methods=["POST"])
def upload():
    if "user" not in session:
        return redirect("/login")
    file = request.files["file"]
    if file.filename == "":
        return redirect("/")
    username = session["user"]
    user_path = os.path.join(UPLOAD_FOLDER, username, file.filename)
    file.save(user_path)
    return redirect("/")

@app.route("/uploads/<filename>")
def view_file(filename):
    if "user" not in session:
        return redirect("/login")
    username = session["user"]
    return send_from_directory(os.path.join(UPLOAD_FOLDER, username), filename)

@app.route("/delete/<filename>")
def delete_file(filename):
    if "user" not in session:
        return redirect("/login")
    username = session["user"]
    file_path = os.path.join(UPLOAD_FOLDER, username, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect("/")

if __name__ == "__main__":
    app.run()
