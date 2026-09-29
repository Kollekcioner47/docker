#!/usr/bin/env python3
"""Приложение «Заметки»: Flask и PostgreSQL (практика 6)."""

import os

import psycopg
from flask import Flask, redirect, render_template_string, request, url_for

app = Flask(__name__)

DB = {
    "host": os.environ.get("POSTGRES_HOST", "db"),
    "port": os.environ.get("POSTGRES_PORT", "5432"),
    "dbname": os.environ.get("POSTGRES_DB", "notes"),
    "user": os.environ.get("POSTGRES_USER", "notes"),
    "password": os.environ.get("POSTGRES_PASSWORD", ""),
}

PAGE = """<h1>Заметки</h1>
<form method="post"><input name="note" placeholder="Новая заметка" required>
<button type="submit">Добавить</button></form>
<ul>{% for note in notes %}<li>{{ note }}</li>{% endfor %}</ul>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    with psycopg.connect(**DB) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS notes (content text)")
        if request.method == "POST":
            conn.execute("INSERT INTO notes (content) VALUES (%s)",
                         (request.form["note"],))
            return redirect(url_for("index"))
        notes = conn.execute("SELECT content FROM notes").fetchall()
    return render_template_string(PAGE, notes=notes)


@app.route("/healthz")
def healthz():
    try:
        with psycopg.connect(**DB) as conn:
            conn.execute("SELECT 1")
    except psycopg.Error:
        return "database error\n", 503
    return "ok\n"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
