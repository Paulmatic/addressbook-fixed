# Use official Python image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/code

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /code

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create staticfiles directory
RUN mkdir -p /code/staticfiles && \
    chown -R 1000:1000 /code/staticfiles

# Run collectstatic as non-root user
USER 1000
RUN python manage.py collectstatic --noinput

# Run application
CMD ["gunicorn", "addressbook.wsgi:application", "--bind", "0.0.0.0:8000"]