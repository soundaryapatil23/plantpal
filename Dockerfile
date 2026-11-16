# Deployment enhancement: MULTI-STAGE build.
# Stage 1 installs dependencies; stage 2 is a slim runtime without pip caches/build tooling.

# ---------- Stage 1: build ----------
FROM python:3.12-slim AS builder
WORKDIR /build
COPY app/requirements.txt .
# pytest is only needed in CI, so it is excluded from the runtime image
RUN grep -v '^pytest' requirements.txt > runtime-requirements.txt \
 && pip install --no-cache-dir --prefix=/install -r runtime-requirements.txt

# ---------- Stage 2: runtime ----------
FROM python:3.12-slim
ENV APP_PORT=5000 \
    APP_VERSION=1.0.0 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/app.py .
RUN useradd --no-create-home appuser
USER appuser
EXPOSE 5000
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${APP_PORT} app:app"]
