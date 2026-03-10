FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3001

CMD ["sh", "-c", "python manage.py migrate && gunicorn web_bff.wsgi:application --bind 0.0.0.0:3001"]
