# 🤖 AI 챗봇

HuggingFace의 Qwen 모델을 활용한 AI 챗봇 웹 애플리케이션입니다.

## 🌐 배포 주소

| 서비스 | URL |
|--------|-----|
| 백엔드 API | https://two026-chatbot-backend-v2ys.onrender.com |
| GitHub | https://github.com/byunhyein/chatbot |

## 🛠 기술 스택

### Frontend
- **React 19** — UI 라이브러리
- **Vite 8** — 빌드 도구
- **React Compiler** — 자동 최적화 (babel-plugin-react-compiler)

### Backend
- **FastAPI** — Python 웹 프레임워크
- **Uvicorn** — ASGI 서버
- **HuggingFace Inference API** — AI 모델 호출 (`Qwen/Qwen3-4B-Instruct-2507`)
- **Render** — 백엔드 호스팅

## 📁 프로젝트 구조

```
chatbot/
├── frontend/          # React + Vite 프론트엔드
│   ├── src/
│   │   ├── App.jsx    # 메인 챗봇 UI
│   │   ├── index.css  # 스타일
│   │   └── main.jsx   # 엔트리포인트
│   ├── index.html
│   └── package.json
│
└── backend/           # FastAPI 백엔드
    ├── main.py        # API 서버 (GET /, POST /chat)
    ├── requirements.txt
    └── .env           # HF_TOKEN 환경변수
```

## 🚀 로컬 실행 방법

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt

# .env 파일에 HuggingFace 토큰 설정
# HF_TOKEN=your_token_here

uvicorn main:app --reload --port 8001
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

> 로컬 실행 시 `src/App.jsx`의 API 주소를 `http://127.0.0.1:8001/chat` 으로 변경하세요.

## 📡 API 명세

### `GET /`
서버 상태 확인

**Response:**
```json
{ "message": "백엔드 정상 작동 중" }
```

### `POST /chat`
AI에게 메시지 전송

**Request Body:**
```json
{ "text": "안녕하세요!" }
```

**Response:**
```json
{ "reply": "안녕하세요! 무엇을 도와드릴까요?" }
```

## 🔐 환경 변수

| 변수명 | 설명 |
|--------|------|
| `HF_TOKEN` | HuggingFace API 토큰 |
