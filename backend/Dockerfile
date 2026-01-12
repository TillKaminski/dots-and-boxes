FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

FROM python:3.12-slim
ENV PATH="/usr/local/bin:$PATH" PYTHONUNBUFFERED=1

RUN apt-get update && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN addgroup -gid 1000 app && useradd --uid 1000 --gid 1000 -m app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app
COPY --chown=app:app . .

USER app
EXPOSE 8000

CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8000", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker"]
