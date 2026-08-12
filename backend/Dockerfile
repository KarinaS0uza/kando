FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Placeholder values just so collectstatic can boot Django during the build;
# Render injects the real env vars at container runtime, overriding these.
ENV DJANGO_SECRET_KEY=build-time-placeholder \
    DJANGO_DEBUG=False \
    DJANGO_ALLOWED_HOSTS=localhost

RUN python manage.py collectstatic --noinput

CMD gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --timeout 240 --workers 1
