#!/usr/bin/env python3
"""Учебное приложение практики 10 «Безопасность образов и сканирование».

Приложение намеренно написано только на стандартной библиотеке Python.
Причины две, и обе практические:

  * сборка образа не требует доступа в интернет: на учебном стенде сеть
    есть не всегда, а занятие не должно срываться из-за недоступного PyPI;
  * в образ не попадает ни одного стороннего пакета. Для практики
    про безопасность образов это важно: каждую уязвимость, найденную
    сканером, можно объяснить базовым образом, а не зависимостями
    приложения.

Точка /whoami отдаёт uid и gid процесса. Это нужно затем, чтобы
проверить непривилегированный запуск там, где нет shell: в минимальных
образах (distroless) команду id выполнить нечем, а приложение отвечает
на вопрос «от кого я работаю» всегда.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "8080"))
VERSION = os.environ.get("APP_VERSION", "1.0")


def identity():
    """Кто мы есть с точки зрения ядра: uid, gid и признак root."""
    return {
        "uid": os.getuid(),
        "gid": os.getgid(),
        "pid": os.getpid(),
        "is_root": os.getuid() == 0,
        "version": VERSION,
    }


class Handler(BaseHTTPRequestHandler):
    """Минимальный обработчик: три маршрута, ни одной зависимости."""

    server_version = "p10-demo"
    sys_version = ""

    def do_GET(self):
        if self.path == "/healthz":
            self.answer(200, {"status": "ok"})
        elif self.path == "/whoami":
            self.answer(200, identity())
        else:
            self.answer(200, {
                "message": "hello from the hardened image",
                "uid": os.getuid(),
                "version": VERSION,
            })

    def answer(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        """Пишем в журнал одну короткую строку вместо трёх.

        Так журнал контейнера остаётся читаемым: при проверке
        работоспособности каждые тридцать секунд в него попадает запрос,
        и стандартный формат с датой в локальном времени быстро
        превращает журнал в мусор.
        """
        sys.stderr.write("%s %s\n" % (self.command, self.path))


def main():
    # Печатаем, от кого работаем, ещё до открытия порта: если контейнер
    # запущен от root, это видно в журнале сразу, а не после разбора.
    sys.stderr.write("start uid=%d gid=%d version=%s\n"
                     % (os.getuid(), os.getgid(), VERSION))

    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
