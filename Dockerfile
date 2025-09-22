FROM python:3.12-slim-bullseye

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

# Встановіть залежності для WeasyPrint + gcc
RUN apt-get update && apt-get install -y \
    gcc \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Виконуємо тільки collectstatic під час build
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Виконуємо migrate перед запуском Gunicorn
ENTRYPOINT [ "/bin/sh", "-c", "python manage.py migrate && gunicorn resume_builder.wsgi -b 0.0.0.0:8000"]