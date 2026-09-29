# Образ frontend-сервиса: nginx, который проксирует запросы на backend.
#
# Почему nginx работает не от root и слушает 8080, а не 80:
# мастер-процессу nginx права root нужны ровно для двух вещей —
# занять порт ниже 1024 и записать pid-файл. Порт наружу публикует
# Swarm, поэтому внутри контейнера вполне достаточно 8080, а от root
# можно отказаться. Это не теория: непривилегированный пользователь
# в контейнере — половина защиты от побега из контейнера (практика 10).
FROM nginx:1.30-alpine

# В образе nginx pid-файл и каталог временных файлов принадлежат root:
# под пользователем nginx мастер-процесс не сможет их создать и упадёт
# с «permission denied». Готовим их заранее, при сборке.
RUN mkdir -p /var/cache/nginx \
    && touch /var/run/nginx.pid \
    && chown -R nginx:nginx /var/cache/nginx /var/run/nginx.pid

# Конфигурация сайта: слушает 8080, проксирует на сервис backend,
# отдаёт /healthz для healthcheck из файла стека.
COPY default.conf /etc/nginx/conf.d/default.conf

USER nginx

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD ["wget", "--spider", "-q", "http://127.0.0.1:8080/healthz"]

CMD ["nginx", "-g", "daemon off;"]
