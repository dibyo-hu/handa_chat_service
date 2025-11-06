# main.py
import json
import asyncio
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional

from chat_service import chat_service, system_prompt_cache
# from db_utils import fetch_user_context_from_postgres   # uncomment when DB ready

app = FastAPI(title="Gemini Streaming Chat Service")

# Dummy context provider (for now)
async def fetch_user_context_dummy(user_id: Optional[str]):
    if not user_id:
        return None
    # small JSON-bucket matching your JSONB schema
    return {
        "user_id": user_id,
        "name": "DUMMY_" + user_id,
        "account_summary": {"acc1_latest_balance": 29728.6, "acc2_latest_balance": 318866},
        "preferences": {"risk_profile": "moderate"}
    }

@app.post("/admin/system-prompt")
async def set_system_prompt(prompt: str = Form(...)):
    """Admin only: update cached system prompt. Secure this endpoint in prod."""
    await system_prompt_cache.refresh(prompt)
    return {"status": "ok", "message": "system prompt cached"}

@app.post("/chat")
async def chat(message: str = Form(...), user_id: Optional[str] = Form(None), rag_docs: Optional[str] = Form(None)):
    """
    Non-streaming chat endpoint.
    rag_docs: optional JSON string representing list of short doc snippets.
    """
    try:
        # swap to real DB fetch later
        user_context = await fetch_user_context_dummy(user_id)
        rag_list = json.loads(rag_docs) if rag_docs else None
        resp = await chat_service.send_single(message, user_context=user_context, rag_docs=rag_list)
        return {"response": resp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(request: Request, message: str = Form(...), user_id: Optional[str] = Form(None), rag_docs: Optional[str] = Form(None)):
    """
    Streaming endpoint using text/event-stream (SSE friendly).
    The UI can listen to 'data:' events, and final 'done' event.
    """

    async def event_generator():
        try:
            user_context = await fetch_user_context_dummy(user_id)
            rag_list = json.loads(rag_docs) if rag_docs else None

            # stream chunks
            async for chunk in chat_service.send_stream(message, user_context=user_context, rag_docs=rag_list):
                # SSE format
                yield f"data: {chunk}\n\n"
                if await request.is_disconnected():
                    break

            # final event
            yield "event: done\ndata: <EOF>\n\n"
        except asyncio.CancelledError:
            return
        except Exception as exc:
            yield f"event: error\ndata: {str(exc)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
