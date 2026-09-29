# Образ backend-сервиса приложения «Заметки» (практика 7).
#
# Почему зависимости ставятся обычным pip, без apt и компилятора:
# драйвер базы — PyMySQL, он написан на чистом Python. Прежняя версия
# курса использовала mysqlclient, из-за которого в образ приходилось
# тащить gcc, pkg-config и заголовки MySQL: образ вырастал в разы,
# сборка шла минутами, а в финальном образе оставался компилятор.
FROM python:3.13-slim

LABEL org.opencontainers.image.title="notes-backend" \
      org.opencontainers.image.description="Backend приложения Заметки для практики 7"

# PYTHONDONTWRITEBYTECODE — не писать .pyc внутрь образа: они не нужны,
# а слой от них только толще.
# PYTHONUNBUFFERED — не буферизовать вывод. Без этого строки приложения
# появляются в docker service logs с задержкой, и кажется, что сервис
# молчит, хотя он работает.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Сначала только список зависимостей, потом код. Так слой с установкой
# библиотек переиспользуется из кэша, пока requirements.txt не менялся,
# и правка одной строки в app.py не тянет за собой повторную установку
# Flask (практика 3).
COPY requirements.txt ./
RUN pip install --no-cache-dir --requirement requirements.txt

COPY app.py ./

# Пользователь без прав root. UID задан числом намеренно: в образе
# нет записи в /etc/passwd под произвольное имя, а числовой UID
# одинаково понимают и docker run, и задачи Swarm (практика 10).
RUN useradd --create-home --uid 10001 notes

USER notes

EXPOSE 5000

# HEALTHCHECK нужен и одиночному контейнеру, и сервису: по нему Swarm
# понимает, что задача готова принимать запросы, а не просто запущена.
# Проверяем свой же адрес /healthz — без обращения к базе: иначе
# недоступная база выглядела бы как неработающий backend, и Swarm
# перезапускал бы не тот сервис.
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import urllib.request as u; u.urlopen('http://127.0.0.1:5000/healthz', timeout=3)"]

# exec-форма: приложение получает сигналы напрямую от Docker,
# а не через промежуточную оболочку (практика 3).
CMD ["python", "app.py"]
