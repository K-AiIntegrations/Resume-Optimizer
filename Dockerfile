FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# If your file is named "requirements" (no .txt), use the 2 lines marked (B).
# --- (A) if your file is requirements.txt:
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
# --- (B) if your file is literally named "requirements":
# COPY requirements /app/requirements
# RUN pip install --no-cache-dir -r /app/requirements

# App code
COPY app /app/app

# Ensure runtime dirs always exist even if empty
RUN mkdir -p /app/files /app/static

EXPOSE 10000
CMD ["sh","-c","uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
