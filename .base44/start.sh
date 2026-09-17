#!/usr/bin/env bash
set -e

cd /app/python

# Install uv and sync the SDK from local source
pip install --quiet uv
uv sync --prerelease=if-necessary-or-explicit

# Install web app dependencies
uv pip install fastapi uvicorn

# Start the FastAPI app with live reload on port 3000
exec uv run uvicorn web_app.main:app \
  --host 0.0.0.0 \
  --port 3000 \
  --reload \
  --reload-dir /app/python/web_app \
  --app-dir /app/python
