#!/usr/bin/env python3
"""Backend приложения «Заметки» — практика 7 курса по Docker.

На что обратить внимание при чтении файла:

  * пароль к базе читается из файла /run/secrets/mysql_password,
    а не из переменной окружения: переменную видно в docker inspect
    и в /proc/1/environ внутри контейнера. Разбор — практика 9;
  * подключение к базе повторяется с паузами. В Swarm база и приложение
    стартуют одновременно, и «MySQL ещё не готова» — нормальная
    ситуация, а не повод упасть и перезапускаться по кругу;
  * есть адрес /healthz: по нему healthcheck из файла стека решает,
    готова ли задача принимать запросы.
"""

import os
import time
from contextlib import contextmanager

import pymysql
from flask import Flask, redirect, render_template_string, request, url_for

app = Flask(__name__)

# Страница собирается строкой, без каталога templates: приложение
# учебное, и лишний файл в образе — это лишний слой и лишний вопрос
# «а где он лежит». Внешний CSS не подключаем намеренно: у лаборатории
# может не быть выхода в интернет, а страница должна открываться всегда.
PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Заметки в Docker Swarm</title>
</head>
<body>
  <h1>Заметки</h1>
  <form method="post" action="/">
    <input type="text" name="note" size="60" required>
    <button type="submit">Добавить</button>
  </form>
  <ul>
    {% for note_id, body in notes %}
    <li>{{ body }} <small>#{{ note_id }}</small></li>
    {% else %}
    <li>Пока ни одной заметки.</li>
    {% endfor %}
  </ul>
</body>
</html>
"""


def secret(variable, fallback=""):
    """Возвращает значение переменной или файла секрета.

    Если задана переменная с суффиксом _FILE (так делают секреты Swarm
    и официальные образы postgres и mysql), значение читается из файла.
    Разница видна в docker inspect: у переменной видно само значение,
    у файла — только путь, и пути достаточно, чтобы никто не подсмотрел
    пароль в описании контейнера.
    """
    path = os.environ.get(variable + "_FILE")
    if path:
        with open(path, encoding="utf-8") as handle:
            return handle.read().strip()
    return os.environ.get(variable, fallback)


# Параметры подключения к базе. Значения по умолчанию нужны, чтобы
# приложение можно было запустить вручную, вне Swarm, и не получить
# ошибку на пустой переменной.
DB = {
    "host": os.environ.get("MYSQL_HOST", "db"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "user": os.environ.get("MYSQL_USER", "notes"),
    "database": os.environ.get("MYSQL_DATABASE", "notes"),
}


def connect(attempts=10, delay=3):
    """Подключается к базе, повторяя неудачные попытки.

    Почему не «упасть и перезапуститься»: при первом запуске MySQL
    инициализирует каталог данных, и на это уходят десятки секунд.
    Задача, которая в этот момент выходит с кодом 1, заставляет Swarm
    перезапускать её снова и снова, забивая журнал одинаковыми
    ошибками. Пара лишних попыток решает проблему целиком.
    """
    last_error = None
    for number in range(1, attempts + 1):
        try:
            return pymysql.connect(
                password=secret("MYSQL_PASSWORD"),
                charset="utf8mb4",
                **DB,
            )
        except pymysql.Error as error:
            last_error = error
            app.logger.warning("база недоступна (попытка %d): %s", number, error)
            time.sleep(delay)
    raise RuntimeError("не удалось подключиться к базе: %s" % last_error)


@contextmanager
def database():
    """Соединение с базой на время одного HTTP-запроса.

    Почему новое соединение на каждый запрос, а не одно на всё
    приложение: реплик backend несколько, задачи Swarm перезапускаются
    и переезжают между узлами. Долгоживущее соединение рано или поздно
    окажется закрытым со стороны базы, и приложение начнёт отвечать
    ошибкой, пока его не перезапустят руками.
    """
    connection = connect()
    try:
        yield connection
    finally:
        connection.close()


@app.route("/healthz")
def healthz():
    """Ответ для healthcheck из файла стека.

    К базе обращаемся не здесь, а в обработчике страницы: healthcheck
    отвечает на вопрос «жив ли этот контейнер», а не «работает ли
    всё приложение целиком». Проверка доступности базы — это
    готовность, и её место в мониторинге, а не в перезапуске задачи.
    """
    return "ok\n", 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/", methods=["GET", "POST"])
def index():
    """Показывает список заметок и принимает новую."""
    if request.method == "POST":
        note = (request.form.get("note") or "").strip()
        if note:
            with database() as connection:
                with connection.cursor() as cursor:
                    # Параметры передаются отдельно от текста запроса:
                    # подстановка строки в SQL — это SQL-инъекция,
                    # и учебный пример не должен ей учить.
                    cursor.execute("INSERT INTO notes (body) VALUES (%s)", (note,))
                connection.commit()
        return redirect(url_for("index"))

    with database() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, body FROM notes ORDER BY id")
            notes = cursor.fetchall()

    return render_template_string(PAGE, notes=notes)


if __name__ == "__main__":
    # Отладочный сервер Flask. Для стенда и для проверки стека его
    # достаточно; почему в курсе не gunicorn — написано в README
    # рядом с файлами практики.
    app.run(host="0.0.0.0", port=5000)
