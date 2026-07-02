FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements/ ./requirements/


RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
    --default-timeout=3000 \
    --retries 20 \
    -r requirements/dev.txt


COPY manage.py /app/
COPY config/ /app/config/
COPY apps/ /app/apps/
COPY templates/ /app/templates/
COPY static/ /app/static/
COPY package.json /app/

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]