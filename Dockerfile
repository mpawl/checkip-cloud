FROM python:3.15.0-slim

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir --require-hashes -r requirements.txt

COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
