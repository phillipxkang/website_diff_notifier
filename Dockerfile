FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app
COPY pyproject.toml .
RUN uv sync --frozen

COPY . .
# Ensure we use the virtualenv created by uv
ENV PATH="/app/.venv/bin:$PATH"
