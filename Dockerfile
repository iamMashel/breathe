FROM python:3.13-slim

WORKDIR /app

# Copy uv binary from official distroless image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install deps into system Python (no venv needed in Docker)
ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1

# Layer cache: install dependencies before copying app code
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application
COPY app/ ./app/

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
