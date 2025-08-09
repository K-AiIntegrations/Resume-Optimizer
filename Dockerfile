FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# If your file is named `requirements` instead of `requirements.txt`, change the two lines below accordingly.
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# App code
COPY app /app/app

# Ensure these exist even if empty, so COPY/Mounts never fail
RUN mkdir -p /app/files /app/static

EXPOSE 10000
# Use ${PORT} provided by Render; default to 10000 locally
CMD ["sh","-c","uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
