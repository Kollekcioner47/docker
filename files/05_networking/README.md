# Практика 5. Порты и сети Docker

В этом каталоге лежит только то, что описывается файлом. Все команды
практики студент набирает сам — готовых скриптов здесь нет.

| Файл | Что это |
|---|---|
| `app-network.yml` | Лаборатория практики, описанная файлом Compose |

Что в файле: сеть `p5-net` (драйвер `bridge`, имя задано явно), сервер
`p5-nginx` с публикацией на `127.0.0.1:8080`, клиент `p5-client` в той же
сети и `p5-isolated` в сети по умолчанию. Это ровно тот же стенд, который
в практике собирается командами `docker run` и `docker network create`.

## Как запустить

```bash
cd files/05_networking
docker compose -f app-network.yml up -d
docker compose -f app-network.yml ps
docker exec p5-client ping -c 2 p5-nginx
docker exec p5-client wget -q -O - http://p5-nginx | head -2
docker compose -f app-network.yml down
```

Сеть создаётся сама и называется `p5-net` — так же, как в практике:
сети, которые делает Compose, и сети из команды `docker network create` —
это одно и то же.

## Про публикацию порта

Порт записан как `"127.0.0.1:8080:80"`, а не как `8080:80`. Без адреса
в начале Docker открыл бы порт на `0.0.0.0` — на всех интерфейсах машины,
включая внешний. С самой машины проверка работает так же:

```bash
curl -I http://127.0.0.1:8080
```

## Уборка

```bash
docker rm -f p5-nginx p5-client p5-isolated
docker network rm p5-net
```

`docker network prune` для этого не нужен: он удаляет все сети, к которым
не подключён ни один контейнер, — в том числе чужие и остановленные.
