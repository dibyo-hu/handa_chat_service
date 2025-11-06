# 🧠 Handa Uncle – Gemini-Driven Financial Opinion Backend (FastAPI)

## Purpose

A modular backend service for streaming AI-driven financial insights, powered by **Google Gemini** (`google-genai` SDK).  
The design supports system prompt caching, user context injection (from DB), and RAG augmentation — with an easy migration path to a TypeScript/GCP-native version later.

---

## 🧩 Overview

This backend provides two chat endpoints (`/chat` and `/chat/stream`) built on top of Gemini’s async API using the official `google-genai` SDK.

**Features:**
- Stream AI responses in Server-Sent Events (SSE) format.
- Dynamically include:
  - System Prompt (cached for efficiency)
  - User Context (fetched from DB)
  - RAG documents (retrieved by another service)
- Clean handoff point for DB integration and TypeScript migration.

---

## 🧱 Architecture

### Core Files

| File             | Purpose                                                               |
|------------------|-----------------------------------------------------------------------|
| main.py          | FastAPI app with chat endpoints and dummy DB context                  |
| chat_service.py  | Handles Gemini API, prompt building, and system prompt caching        |
| db_utils.py      | (To be implemented) Fetches user context JSONB from PostgreSQL        |
| .env             | Stores secrets like GENAI_API_KEY, DB URL, and model config           |
| test.py          | Simple local streaming test using aiohttp                             |


### ⚙️ Flow Diagram

A[User Request] --> B{POST /chat or /chat/stream}
  B --> C["Fetch user context (dummy or real DB)"]
  C --> D["Merge system prompt + user context + RAG docs + user message"]
  D --> E["Build composite prompt (text-only)"]
  E --> F[Send to Gemini via ChatService]
  F --> G["Stream chunks back (if /chat/stream)"]
  G --> H[Response to client]

---

## 📁 File-Level Breakdown

### 1️⃣ chat_service.py

Handles interaction with Gemini and system prompt caching.

#### Key Components

- **SystemPromptCache**
  - Caches system prompt in memory for 5 minutes (TTL = 300s).
  - Avoids re-sending long instructions each time.
  - Future-friendly for centralized cache (Redis/Cloud Memorystore).

- **build_prompt()**
  - Combines:
    - System Prompt
    - User Context (compact JSON)
    - RAG Docs (list of short text snippets)
    - User Message
  - Produces a plain-text message for the LLM.

- **ChatService**
  - Wraps Gemini client calls:
    - `send_single()` — full response (non-streaming)
    - `send_stream()` — async generator for SSE
  - Uses official `google.genai.Client`.
  - **Important:**
    - Streaming is handled via async iterator, so do not block event loop.
    - `_create_chat()` returns an AsyncChat — no await needed for creation.
    - `send_message_stream()` must be awaited once before iteration.

---

### 2️⃣ main.py

The FastAPI entrypoint.

#### Endpoints

| Endpoint                   | Description                                         |
|----------------------------|----------------------------------------------------|
| POST `/chat`               | Standard request-response chat (non-streaming).    |
| POST `/chat/stream`        | Streams Gemini output chunk by chunk (SSE).        |
| POST `/admin/system-prompt`| Updates in-memory system prompt cache (admin-only) |

#### Behavior

- `fetch_user_context_dummy()` simulates DB output for now.
- Once DB is connected, replace it with:
    ```python
    from db_utils import fetch_user_context_from_postgres
    user_context = await fetch_user_context_from_postgres(user_id)
    ```
- `StreamingResponse` yields partial tokens in real time.
- UI/frontend client must use EventSource or streaming parser to consume.

---

### 3️⃣ db_utils.py

Database helper for future integration.

**Expected Table:**
```sql
CREATE TABLE user_contexts (
  user_id TEXT PRIMARY KEY,
  ctx JSONB NOT NULL
);
```

**Function:**
```python
async def fetch_user_context_from_postgres(user_id: str) -> Optional[Dict[str, Any]]:
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        row = await conn.fetchrow("SELECT ctx FROM user_contexts WHERE user_id = $1", user_id)
        if row:
            return row["ctx"]
        return None
    finally:
        await conn.close()
```

**Integration:**
Replace dummy fetcher in `main.py`:
```python
user_context = await fetch_user_context_from_postgres(user_id)
```

---

### 4️⃣ test.py

Quick test script to validate streaming behavior.

**How to run:**
1. Start the FastAPI server:
   ```
   uvicorn main:app --reload
   ```
2. Then execute:
   ```
   python3 test.py
   ```

You should see:
```
data: Let's analyze your financial behavior...
data: You show moderate spending discipline...
event: done
data: <EOF>
```

---

## 🧠 Adding RAG Integration

- RAG docs are passed in as JSON list:
  ```json
  ["User's portfolio shows 40% tech exposure", "Last SIP update 30 days ago"]
  ```
- Later, backend developer should:
  - Fetch RAG docs via retrieval microservice/vector DB.
  - Pass into `/chat` or `/chat/stream` as:
    ```python
    rag_docs=json.dumps(retrieved_snippets)
    ```
- `build_prompt()` already knows how to inject them.

---

## 🔒 Environment Setup

**.env**
```env
GENAI_API_KEY="your_google_genai_api_key_here"
GENAI_MODEL="gemini-1.5-pro-latest"
DATABASE_URL="postgresql://user:pass@localhost:5432/yourdb"
```

**Install dependencies:**
```
pip install fastapi uvicorn google-genai aiohttp asyncpg python-dotenv
```

**Run FastAPI server:**
```
uvicorn main:app --reload
```

---

## 🚀 Migration to TypeScript (for GCP-native backend)

Your dev plans to migrate to TypeScript later (probably using `@google/genai` NPM SDK).

| Python Concept                | TypeScript Equivalent                                 | Notes                                       |
|-------------------------------|------------------------------------------------------|---------------------------------------------|
| `google.genai.Client`         | `import { GoogleGenerativeAI } from "@google/genai"` | `new GoogleGenerativeAI({ apiKey })`        |
| `client.aio.chats.create()`   | `client.startChat({ model, history })`               | Both maintain conversation state            |
| `send_message_stream()`       | `chat.sendMessageStream()` (async iterator)          | AsyncIterable in TS                         |
| `StreamingResponse`           | Node.js `Response` with `ReadableStream`/SSE         | Must flush manually for SSE                 |
| `SystemPromptCache` (memory)  | In-memory LRU or Redis                               | Use TTL cache libraries                     |
| `asyncpg`                     | `pg` or `drizzle-orm`                               | Use connection pooling/async/await          |
| `.env` loading                | `dotenv`                                             | Same key structure                          |

**TypeScript Streaming Example:**
```typescript
const stream = await chat.sendMessageStream(prompt);
for await (const chunk of stream) {
  process.stdout.write(chunk.text || "");
}
```

> ⚠️ **Caveat:**  
> Node must be run with native async iteration over streams enabled (Node 18+).  
> Use `for await...of` or `.on('data')` depending on your HTTP library.

---

## 🧩 Extension Points

| Feature               | Integration Point                                                                       |
|-----------------------|----------------------------------------------------------------------------------------|
| 🔄 RAG (Vector Search)| Modify `/chat/stream` → call your retrieval API, then pass docs                        |
| 💾 Persistent History | Add Redis / Firestore → store chat history by `user_id`                                |
| 🔐 Auth               | Add bearer token or session middleware                                                 |
| 📊 Logging            | Insert middleware (FastAPI/Express) for chunk timing & latency                         |
| 🧭 Monitoring         | Wrap Gemini calls with timing metrics (Prometheus, Datadog, etc.)                      |

---

## 🧠 Developer Notes

- The system prompt is cached — update it via `/admin/system-prompt` POST form.
- System prompt, context, and RAG are all textually merged before hitting model.
- SSE (streaming) is line-buffered, so UI must parse events starting with `data:` and event `done`.
- Gemini’s SDK methods are async-safe — **never block the event loop inside `async for`**.
- Keep prompt construction deterministic; avoid injecting dynamic `datetime.now()` or random text in production unless justified.

---

## ✅ Quick Validation Checklist

| Check                             | Expected Result           |
|------------------------------------|--------------------------|
| `/chat` responds with JSON         | ✅                       |
| `/chat/stream` streams chunks (SSE)| ✅                       |
| `/admin/system-prompt` updates     | ✅                       |
| .env loads key correctly           | ✅                       |
| Dummy DB replaced with real one    | 🟡 (when DB ready)        |
| RAG integrated                     | 🟡 (when retriever ready) |

---

## ✨ Final Words

The codebase is **modular, streaming-safe, and RAG-ready**.  
All your backend dev needs to do is:
- Swap `fetch_user_context_dummy → fetch_user_context_from_postgres`
- Plug RAG service response → `rag_docs`
- Migrate prompt construction logic to TS (same structure)
- Keep streaming structure identical (async iterator loop)
