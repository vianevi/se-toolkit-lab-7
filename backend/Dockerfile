# Adapted from https://github.com/astral-sh/uv-docker-example
# Modified to avoid read-only uv.lock issue

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# First copy workspace files
COPY pyproject.toml uv.lock ./
COPY backend/pyproject.toml ./backend/

# Sync dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project

# Copy the rest of the backend
COPY backend /app/backend

# Sync again with all files
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

# ---
# Stage 2: use a final image without uv
# ---

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

COPY --from=builder --chown=nonroot:nonroot /app /app

ENV PATH="/app/.venv/bin:$PATH"

USER nonroot

WORKDIR /app

CMD ["sh", "-c", "python backend/app/run.py"]
