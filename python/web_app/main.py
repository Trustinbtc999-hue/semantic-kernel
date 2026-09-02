"""FastAPI web app that streams Semantic Kernel chat responses in real time."""

import json
import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.contents import ChatHistory

# --- Kernel setup -----------------------------------------------------------

kernel = Kernel()
kernel.add_service(
    OpenAIChatCompletion(
        service_id="chat",
        ai_model_id=os.getenv("OPENAI_CHAT_MODEL_ID", "gpt-4o"),
    )
)

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful AI assistant powered by Microsoft Semantic Kernel. "
    "Be concise, friendly, and informative."
)

# --- App --------------------------------------------------------------------

app = FastAPI(title="Semantic Kernel Chat")

HTML_PATH = os.path.join(os.path.dirname(__file__), "static", "index.html")


@app.get("/lab")
async def lab_redirect():
    """Redirect old Jupyter path to the chat app."""
    return RedirectResponse(url="/", status_code=302)


@app.get("/", response_class=HTMLResponse)
async def index():
    with open(HTML_PATH, encoding="utf-8") as f:
        return f.read()


@app.post("/api/chat")
async def chat(request: Request):
    """Stream a Semantic Kernel chat response as Server-Sent Events."""
    body = await request.json()
    messages = body.get("messages", [])
    system_prompt = body.get("system_prompt") or DEFAULT_SYSTEM_PROMPT

    # Rebuild ChatHistory from the conversation the client sends.
    chat_history = ChatHistory(system_message=system_prompt)
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "user":
            chat_history.add_user_message(content)
        elif role == "assistant":
            chat_history.add_assistant_message(content)

    settings = OpenAIChatPromptExecutionSettings()

    async def event_stream():
        try:
            async for chunk in kernel.get_service("chat").get_streaming_chat_message_content(
                chat_history=chat_history,
                settings=settings,
            ):
                if chunk:
                    text = str(chunk)
                    if text:
                        yield f"data: {json.dumps({'content': text})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/api/health")
async def health():
    return {"status": "ok", "model": os.getenv("OPENAI_CHAT_MODEL_ID", "gpt-4o")}
