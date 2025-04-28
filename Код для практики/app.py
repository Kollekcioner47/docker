from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3

app = Flask(__name__)

DB_NAME = 'data.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT)')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if request.method == 'POST':
        note = request.form['note']
        c.execute('INSERT INTO notes (content) VALUES (?)', (note,))
        conn.commit()
        return redirect(url_for('index'))
    c.execute('SELECT id, content FROM notes')
    notes = c.fetchall()
    conn.close()
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Заметки в Docker</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
    <div class="container py-5">
        <h1 class="mb-4 text-center">📝 Мои заметки</h1>
        <form method="post" class="mb-4">
            <div class="input-group">
                <input type="text" name="note" class="form-control" placeholder="Введите новую заметку" required>
                <button class="btn btn-primary" type="submit">Добавить</button>
            </div>
        </form>
        <div class="card shadow">
            <div class="card-body">
                {% if notes %}
                    <ul class="list-group">
                        {% for id, content in notes %}
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                <span>{{ content }}</span>
                                <span class="badge bg-secondary rounded-pill">#{{ id }}</span>
                            </li>
                        {% endfor %}
                    </ul>
                {% else %}
                    <p class="text-muted">Пока нет ни одной заметки...</p>
                {% endif %}
            </div>
        </div>
    </div>
    </body>
    </html>
    ''', notes=notes)

if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=5000)
