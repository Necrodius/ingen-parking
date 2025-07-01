# This Dockerfile sets up a Python environment for a Flask application using Gunicorn as the WSGI server.
# It installs dependencies from a `requirements.txt` file, copies the application code into the container,
# and exposes port 8000 for incoming traffic.

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-8000}"]
