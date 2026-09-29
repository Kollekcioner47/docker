# Секрет, который нужен только сборке.
#
# Токен подключается к одной инструкции RUN монтированием secret
# и живёт ровно столько, сколько она выполняется: ни в слой образа,
# ни в запись о сборке значение не попадает.
#
# Файл с токеном создаётся командой из практики, в курс он не входит:
#
#     docker build --secret id=app_token,src=/tmp/token.txt \
#         -t p9-buildkit .
#     docker history --no-trunc p9-buildkit

FROM alpine:3.24

WORKDIR /opt/app

# Так ставят пакет из закрытого индекса: токен нужен одной команде.
# Здесь вместо обращения к индексу считается отпечаток токена — в образе
# остаётся результат, а самого значения нет. Именно этим секрет сборки
# отличается от ARG: ARG виден в docker history, смонтированный
# секрет — не виден.
RUN --mount=type=secret,id=app_token \
    TOKEN="$(cat /run/secrets/app_token)" && \
    printf '%s\n' "$(printf '%s' "${TOKEN}" | sha256sum | cut -c1-16)" \
        > /opt/app/token-fingerprint

RUN adduser -D -u 10001 app

USER app

# Контейнер печатает отпечаток: так видно, что в образе от секрета
# осталось, а что нет.
CMD ["cat", "/opt/app/token-fingerprint"]
