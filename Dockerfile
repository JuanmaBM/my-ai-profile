FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Copy only metadata first to leverage layer caching for deps
COPY pyproject.toml README.md ./

# Install project and runtime deps (editable install for development)
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir click==8.1.7 typer==0.9.0 && \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir lxml

# Copy the rest of the source
COPY . .

# Default command can be overridden by CI steps
ENTRYPOINT ["python", "cli.py"]
