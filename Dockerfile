FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE = 1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r  requirements.txt

COPY djangoPortfolio/ /app/
COPY .env /app/.env

RUN SECRET_KEY="dummy_for_build" python manage.py collectstatic --noinput
