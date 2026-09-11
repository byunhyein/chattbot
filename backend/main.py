import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import db


load_dotenv(Path(__file__).with_name(".env"))

app = FastAPI()
db.init_db()

allowed_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", "*").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_URL = os.getenv("HF_URL", "https://router.huggingface.co/v1/chat/completions")
HF_MODEL = os.getenv("HF_MODEL", "Qwen/Qwen3-4B-Instruct-2507")
AI_REQUEST_TIMEOUT = int(os.getenv("AI_REQUEST_TIMEOUT", "60"))
AI_RETRY_ATTEMPTS = max(1, int(os.getenv("AI_RETRY_ATTEMPTS", "3")))
AI_RETRY_DELAY_SECONDS = max(0, float(os.getenv("AI_RETRY_DELAY_SECONDS", "2")))
RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}


class Msg(BaseModel):
    text: str


class Title(BaseModel):
    title: str


@app.get("/")
def health_check():
    return {"message": "백엔드 정상 작동 중"}


@app.get("/health")
def render_health_check():
    """Lightweight endpoint for Render uptime checks."""
    return {"status": "ok"}


def _ask_ai_once(history):
    token = os.getenv("HF_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="HF_TOKEN 환경 변수가 설정되지 않았습니다.")

    try:
        response = requests.post(
            HF_URL,
            headers={"Authorization": f"Bearer {token}"},
            json={"model": HF_MODEL, "messages": history, "max_tokens": 1000},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as error:
        raise HTTPException(status_code=502, detail="AI 응답을 가져오지 못했습니다.") from error


def ask_ai(history):
    """Absorb transient failures while the upstream service is waking up."""
    token = os.getenv("HF_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="HF_TOKEN is not configured.")

    last_error = None
    for attempt in range(AI_RETRY_ATTEMPTS):
        try:
            response = requests.post(
                HF_URL,
                headers={"Authorization": f"Bearer {token}"},
                json={"model": HF_MODEL, "messages": history, "max_tokens": 1000},
                timeout=AI_REQUEST_TIMEOUT,
            )
            if response.status_code not in RETRYABLE_STATUS_CODES:
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            last_error = requests.HTTPError(
                f"Temporary AI service error: {response.status_code}", response=response
            )
        except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as error:
            last_error = error

        if attempt < AI_RETRY_ATTEMPTS - 1:
            time.sleep(AI_RETRY_DELAY_SECONDS * (2**attempt))

    raise HTTPException(
        status_code=503,
        detail="AI service is waking up. Please try again shortly.",
        headers={"Retry-After": str(max(1, int(AI_RETRY_DELAY_SECONDS)))},
    ) from last_error


def build_history(session_id):
    return [
        {"role": "user" if row["role"] == "user" else "assistant", "content": row["text"]}
        for row in db.read_message(session_id)
    ]


@app.post("/chat")
def chat(msg: Msg):
    return {"reply": ask_ai([{"role": "user", "content": msg.text}])}


@app.post("/sessions")
def new_session():
    session_id = db.create_session()
    return {"id": session_id, "title": "새 대화"}


@app.get("/sessions")
def list_sessions():
    return {"sessions": db.read_sessions()}


@app.get("/sessions/{session_id}/messages")
def list_messages(session_id: int):
    return {"messages": db.read_message(session_id)}


@app.post("/sessions/{session_id}/messages")
def send_message(session_id: int, msg: Msg):
    first_message = db.count_message(session_id) == 0
    db.create_message(session_id, "user", msg.text)
    if first_message:
        db.update_session(session_id, msg.text[:20])
    reply = ask_ai(build_history(session_id))
    db.create_message(session_id, "bot", reply)
    return {"reply": reply}


@app.put("/sessions/{session_id}")
def rename_session(session_id: int, body: Title):
    title = body.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="제목이 비어 있습니다.")
    if db.update_session(session_id, title) == 0:
        raise HTTPException(status_code=404, detail="해당 대화가 없습니다.")
    return {"id": session_id, "title": title}


@app.delete("/sessions/{session_id}")
def remove_session(session_id: int):
    if db.delete_session(session_id) == 0:
        raise HTTPException(status_code=404, detail="해당 대화가 없습니다.")
    return {"deleted": session_id}
