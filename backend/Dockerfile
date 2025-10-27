FROM python:3.12-alpine AS builder
RUN apk add --no-cache gcc musl-dev linux-headers
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip

FROM python:3.12-alpine
ENV PATH="/usr/local/bin:$PATH" PYTHONUNBUFFERED=1
RUN addgroup -g 1000 app && adduser -u 1000 -G app -s /bin/sh -D app

COPY --from=builder --chown=app:app /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder --chown=app:app /usr/local/bin/ /usr/local/bin/

WORKDIR /app
COPY --chown=app:app . .
USER app

EXPOSE 8000
CMD ["/usr/local/bin/gunicorn", "main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker"]
