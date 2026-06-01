FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements_prod.txt .

RUN pip install --upgrade pip setuptools wheel && \
    pip install \
    --default-timeout=3000 \
    --retries 20 \
    -r requirements_prod.txt

COPY . .


CMD ["python", "manage.py", "runserver", "127.0.0.1:8000"]