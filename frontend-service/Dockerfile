FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Run migrations and start server with SSL
CMD ["sh", "-c", "python manage.py migrate && daphne -e ssl:8000:interface=0.0.0.0:cert=localhost.crt:key=localhost.key api_gateway.asgi:application"]
