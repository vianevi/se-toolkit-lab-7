# Bot Dockerfile
# Uses uv for dependency management (not pip or requirements.txt)
# Build context is the bot/ directory

FROM astral/uv:python3.14-bookworm-slim AS builder

WORKDIR /app

# Copy project file for dependency resolution
COPY pyproject.toml ./

# Install dependencies (no lock file - uv will resolve)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project

# Copy bot source code
COPY . ./bot/

# Runtime stage
FROM python:3.14.2-slim-bookworm

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy bot source code
COPY --from=builder /app/bot /app/bot

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Run the bot
CMD ["python", "bot/bot.py"]
