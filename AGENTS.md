# Base44 Setup Notes — Semantic Kernel

## What this repo is
Microsoft Semantic Kernel — an AI orchestration SDK with Python, .NET, and Java code, plus samples and Jupyter notebooks. It is **not a web application**; there is no built-in web frontend or backend server.

## What runs in the preview
A **Jupyter Lab** server (port 3000) serving `python/samples/` — the SDK's interactive notebooks and sample scripts. The Semantic Kernel Python package is installed in editable mode from local source via `uv`, so edits to `python/semantic_kernel/` are reflected immediately.

## How it was set up
- `docker-compose.base44.yml` — single `jupyter` service on `python:3.12-slim`
- `.base44/start.sh` — installs `uv`, runs `uv sync --extra notebooks`, installs `jupyterlab`, registers the kernel, starts Jupyter Lab
- `.env.base44-defaults` — placeholder model IDs; real `OPENAI_API_KEY` comes from `/run/base44/app.env` (platform-managed secret)

## Secrets
- `OPENAI_API_KEY` — required for notebook cells that call OpenAI models (chat, embeddings). Jupyter itself boots without it, but AI cells will fail. Set via the Base44 secrets dashboard.

## Key env vars (read by SK's pydantic-settings)
- `OPENAI_API_KEY` — API key
- `OPENAI_CHAT_MODEL_ID` — chat model (default: `gpt-4o`)
- `OPENAI_EMBEDDING_MODEL_ID` — embedding model (default: `text-embedding-3-small`)

## Verification
- `curl -sf http://localhost:3000/lab` returns 200
- External Host header also returns 200 (preview proxy works)
- `docker compose -f docker-compose.base44.yml exec -T jupyter sh -c 'printenv OPENAI_API_KEY >/dev/null && echo present'` confirms the secret reached the container

## Restart after changes
- Source code edits: reflected live (editable install + bind mount)
- `start.sh` or compose changes: `docker compose -f docker-compose.base44.yml up -d`
- First boot takes ~60s for `uv sync` + `jupyterlab` install; subsequent restarts are fast (venv persists in bind mount)
