# Build stage
FROM python:3.9-slim as builder

WORKDIR /app
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Runtime stage
FROM python:3.9-slim

WORKDIR /code
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/code \
    PATH="/home/appuser/.local/bin:${PATH}"

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    addgroup --system appuser && \
    adduser --system --ingroup appuser appuser

# Install dependencies first
COPY --from=builder --chown=appuser:appuser /app/wheels /wheels
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir --user /wheels/* && \
    rm -rf /wheels && \
    pip install -r requirements.txt

# Then copy application code
COPY --chown=appuser:appuser . .

# Create staticfiles directory
RUN mkdir -p /code/staticfiles && \
    chown appuser:appuser /code/staticfiles

USER appuser

# Run collectstatic
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "addressbook.wsgi:application", "--bind", "0.0.0.0:8000"]