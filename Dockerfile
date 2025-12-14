FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    git \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Install uv (preferred) - falls back to plain pip usage where needed in the container
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# Create an isolated venv managed by uv
RUN uv venv .venv

# Pre-install core deps needed to run tests in environments where uv cannot parse pyproject
# (Keeps container useful even before project metadata is adjusted.)
RUN uv pip install -p .venv/bin/python -q \
    pytest \
    "typer>=0.12.5" rich rdflib pymupdf Pillow scikit-learn python-docx pytesseract \
    numpy scipy networkx requests regex rapidfuzz

# Default command: print versions
CMD bash -lc "python --version && .venv/bin/python -m pytest -q"

