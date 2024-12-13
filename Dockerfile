FROM python:3.11-slim

# Create a persistent volume for SQLite database
VOLUME ["/data"]

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Make sure the /data directory exists and is writable
RUN mkdir -p /data && chmod 777 /data

# Command to run the application
CMD gunicorn app:app 