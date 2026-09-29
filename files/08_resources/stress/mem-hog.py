#!/usr/bin/env python3
"""Нагрузка на память: просит память блоками, пока контейнер не убьют."""
import sys
import time

block = int(sys.argv[1]) if len(sys.argv) > 1 else 16
chunks = []
while True:
    chunk = bytearray(block * 1024 * 1024)
    # Запись в начало каждой страницы: иначе ядро память не выделит.
    for page in range(0, len(chunk), 4096):
        chunk[page] = 1
    chunks.append(chunk)
    print("занято %d МБ" % (len(chunks) * block), flush=True)
    time.sleep(1)
