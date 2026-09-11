# 🤖 AI 챗봇

HuggingFace의 Qwen 모델을 활용한 AI 챗봇 웹 애플리케이션입니다.

## 🌐 배포 주소

| 서비스 | URL |
|--------|-----|
| 백엔드 API | https://chattbot-back.onrender.com |
| GitHub | https://github.com/byunhyein/chattbot |

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
    ├── .env.example   # 로컬 환경 변수 예시
    └── .env           # 로컬 전용 비밀값 (Git 미추적)
```

## 🚀 로컬 실행 방법

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt

# backend/.env.example을 backend/.env로 복사한 뒤 HF_TOKEN을 입력

uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
# .env.example을 .env.local로 복사하면 로컬 API 주소를 변경할 수 있습니다.
npm run dev
```

> API 주소는 코드가 아니라 환경 변수로 관리합니다. 로컬 기본값은 `http://127.0.0.1:8000`이며, 운영 빌드는 `https://chattbot-back.onrender.com`을 사용합니다.

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
| `HF_URL` | HuggingFace 채팅 API 주소 (선택) |
| `HF_MODEL` | 사용할 HuggingFace 모델 (선택) |
| `FRONTEND_ORIGINS` | 허용할 프론트엔드 Origin 목록 (쉼표 구분, 선택) |
| `VITE_API_BASE_URL` | 프론트엔드가 호출할 백엔드 기본 주소 |
