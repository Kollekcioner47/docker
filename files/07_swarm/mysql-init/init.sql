-- Начальная схема приложения «Заметки» (практика 7).
--
-- Этот файл не копируется на узлы и не лежит рядом со стеком в виде
-- каталога: он передаётся в swarm как config и монтируется в контейнер
-- базы файлом /docker-entrypoint-initdb.d/init.sql. Причина простая:
-- bind mount каталога требует, чтобы каталог был на той машине, где
-- запустится задача, а config приезжает вместе с описанием сервиса.
--
-- ВАЖНО: скрипты из /docker-entrypoint-initdb.d выполняются только
-- при первой инициализации каталога данных, то есть когда база пустая.
-- Если том с данными уже создан, правки в этом файле ни на что
-- не повлияют: схему придётся менять отдельно, руками или миграцией.

CREATE DATABASE IF NOT EXISTS notes
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE notes;

-- utf8mb4, а не utf8: «utf8» в MySQL — это три байта на символ,
-- и заметка с эмодзи или редким иероглифом в неё не поместится.
CREATE TABLE IF NOT EXISTS notes (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  body       VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
