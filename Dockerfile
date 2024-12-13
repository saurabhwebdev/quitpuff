FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Create instance directory
RUN mkdir -p instance && chmod 777 instance

# Initialize database and run migrations
CMD flask db upgrade && gunicorn app:app 