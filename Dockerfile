# syntax=docker/dockerfile:1.6

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=off \
    PYTHONPATH=/app

WORKDIR /app

# =========================
# Builder image
# =========================
FROM base AS builder

ARG INSTALL_DEV=false

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libpq-dev \
        git \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

COPY requirements.txt requirements-dev.txt ./

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && if [ "${INSTALL_DEV}" = "true" ]; then pip install --no-cache-dir -r requirements-dev.txt; fi

COPY . .

# =========================
# Production/runtime image
# =========================
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PATH="/opt/venv/bin:${PATH}" \
    PYTHONPATH=/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

RUN addgroup --system app && adduser --system --ingroup app app \
    && chown -R app:app /app

USER app

EXPOSE 8000

CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000"]

# =========================
# Development image (hot reload)
# =========================
FROM runtime AS dev

ENV ENV=development

CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
