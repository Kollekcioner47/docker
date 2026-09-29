FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./

# Процесс работает не от root, а каталог /app принадлежит root: писать
# туда он не может, поэтому выше и стоит PYTHONDONTWRITEBYTECODE.
RUN useradd --create-home --uid 1000 appuser
USER appuser

EXPOSE 5000
CMD ["python", "app.py"]
