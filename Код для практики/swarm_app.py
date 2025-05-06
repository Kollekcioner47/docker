from flask import Flask, request, redirect, url_for, render_template_string
from flask_mysqldb import MySQL

app = Flask(__name__)

# Настройки подключения к MySQL
app.config['MYSQL_HOST']     = 'db'
app.config['MYSQL_USER']     = 'user'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB']       = 'appdb'

# Инициализация MySQL
mysql = MySQL(app)

# HTML-шаблон с Bootstrap
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Заметки в Docker Swarm</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container py-5">
    <h1 class="mb-4 text-center">📝 Заметки в Swarm</h1>

    <form method="post" action="/" class="mb-4">
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
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = mysql.connection
    cursor = conn.cursor()
    if request.method == 'POST':
        # читаем поле note из формы
        note = request.form.get('note')
        if note:
            cursor.execute("INSERT INTO entries (name) VALUES (%s)", (note,))
            conn.commit()
        return redirect(url_for('index'))

    # GET: читаем все записи
    cursor.execute("SELECT id, name FROM entries ORDER BY id")
    notes = cursor.fetchall()
    cursor.close()

    return render_template_string(HTML_TEMPLATE, notes=notes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
