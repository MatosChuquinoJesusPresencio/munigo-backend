FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py migrate --noinput

EXPOSE 8000

CMD sh -c "gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}"
