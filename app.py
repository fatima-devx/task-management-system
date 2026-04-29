from flask import Flask, render_template, request, jsonify, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

DB = "database.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    completed INTEGER,
    user_id INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        conn.execute(
        "INSERT INTO users (username,password) VALUES (?,?)",
        (username,password)
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username,password)
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            return redirect("/")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/tasks")
def tasks():
    user_id = session["user_id"]

    conn = get_db()
    tasks = conn.execute(
    "SELECT * FROM tasks WHERE user_id=?",
    (user_id,)
    ).fetchall()
    conn.close()

    return jsonify([dict(t) for t in tasks])

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json

    conn = get_db()
    conn.execute(
    "INSERT INTO tasks (title,completed,user_id) VALUES (?,0,?)",
    (data["title"],session["user_id"])
    )
    conn.commit()
    conn.close()

    return jsonify({"status":"ok"})

@app.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"status":"deleted"})

@app.route("/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    data = request.json

    conn = get_db()
    conn.execute(
    "UPDATE tasks SET title=? WHERE id=?",
    (data["title"],id)
    )
    conn.commit()
    conn.close()

    return jsonify({"status":"updated"})

@app.route("/tasks/<int:id>/complete", methods=["PUT"])
def complete(id):
    conn = get_db()
    conn.execute(
    "UPDATE tasks SET completed = NOT completed WHERE id=?",
    (id,)
    )
    conn.commit()
    conn.close()

    return jsonify({"status":"done"})

if __name__ == "__main__":
    app.run(debug=True)