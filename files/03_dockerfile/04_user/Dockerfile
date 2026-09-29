FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8000
RUN useradd --create-home --uid 1000 app
USER app
CMD ["python", "app.py"]
