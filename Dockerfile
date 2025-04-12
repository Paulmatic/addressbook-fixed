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

COPY --from=builder --chown=appuser:appuser /app/wheels /wheels
COPY --chown=appuser:appuser . .

# Install dependencies and clean up
RUN pip install --no-cache-dir --user /wheels/* && \
    rm -rf /wheels && \
    python -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Ensure staticfiles directory exists and has correct permissions
RUN mkdir -p /code/staticfiles && \
    chown appuser:appuser /code/staticfiles

USER appuser

# Collect static files
RUN python manage.py collectstatic --noinput --clear

CMD ["gunicorn", "addressbook.wsgi:application", "--bind", "0.0.0.0:8000"]