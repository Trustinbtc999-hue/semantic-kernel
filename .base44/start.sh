#!/usr/bin/env bash
set -e

cd /app/python

# Install uv and sync the SDK from local source
pip install --quiet uv
uv sync --extra notebooks --prerelease=if-necessary-or-explicit
uv pip install jupyterlab

# Register the kernel
uv run python -m ipykernel install --user --name semantic-kernel --display-name "Semantic Kernel (Python 3.12)"

# Start Jupyter Lab on port 3000, iframe-friendly
exec uv run jupyter lab \
  --ip=0.0.0.0 \
  --port=3000 \
  --no-browser \
  --ServerApp.token="" \
  --ServerApp.password="" \
  --ServerApp.allow_origin="*" \
  --ServerApp.allow_remote_access=True \
  --ServerApp.tornado_settings='{"headers":{"X-Frame-Options":"ALLOWALL","Content-Security-Policy":"frame-ancestors *;"}}' \
  --allow-root \
  --notebook-dir=/app/python/samples
