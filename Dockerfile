# Use official Python image
FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Install Flask and Flask-Session
RUN pip install --no-cache-dir Flask Flask-Session

EXPOSE 8080

ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080

CMD ["flask", "run"]
