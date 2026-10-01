# syntax=docker/dockerfile:1
#
# Multi-stage image for {{cookiecutter.project_name}}.
#   builder: resolves the locked runtime environment (no dev dependencies) with uv.
#   runtime: slim Python image with the virtual environment, the source code and configs/ only.
#            Runs as the non-root user `app`.
#
# Build: make docker-build   (or: docker build -t {{cookiecutter.repo_name}} .)
# Run:   make docker-run ARGS="--help"

# Pinned uv version. Dependabot (docker ecosystem) proposes updates.
FROM ghcr.io/astral-sh/uv:0.12.21 AS uv

# ---- builder ----------------------------------------------------------------
FROM python:{{cookiecutter.python_version}}-slim-trixie AS builder

COPY --from=uv /uv /uvx /bin/

# UV_COMPILE_BYTECODE: compile .pyc files at build time for faster start-up.
# UV_LINK_MODE: copy files from the cache mount (hard links do not work across file systems).
# UV_PYTHON_DOWNLOADS: use the Python interpreter of the base image.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Layer 1: third-party dependencies only. Docker reuses this layer until pyproject.toml or uv.lock changes.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project

# Layer 2: the project itself. README.md is copied because the package metadata can reference it.
COPY README.md ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Example configs, so that `train --config configs/...` works in the container.
COPY configs ./configs

# ---- runtime ----------------------------------------------------------------
FROM python:{{cookiecutter.python_version}}-slim-trixie AS runtime

LABEL org.opencontainers.image.source="{{cookiecutter.repo_url}}" \
      org.opencontainers.image.description="{{ cookiecutter.project_description.replace("$", "\\$") }}"

RUN groupadd --system --gid 1000 app \
    && useradd --system --uid 1000 --gid app --create-home --no-log-init app

WORKDIR /app

# The virtual environment has absolute paths under /app, so it must stay at the same path.
COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER app

CMD ["{{cookiecutter.repo_name}}", "--help"]
