# AI 챗봇

React/Vite 프론트엔드와 FastAPI 백엔드로 구성된 대화형 챗봇입니다. 백엔드는 Hugging Face Inference API의 `Qwen/Qwen3-4B-Instruct-2507` 모델을 호출하고, 대화 기록은 SQLite에 저장합니다.

## 현재 배포 상태

2026-09-11에 확인한 값입니다.

| 항목 | 상태 | 주소 |
| --- | --- | --- |
| 백엔드 API | 배포됨 · `GET /health` HTTP 200 확인 | https://chattbot-back.onrender.com |
| 프론트엔드 | 공개 배포 설정 없음 | 로컬에서만 실행 |
| 소스 저장소 | Git 원격 저장소 | https://github.com/byunhyein/chattbot.git |

프론트엔드는 아직 공개 URL이 없습니다. 다른 사람이 웹에서 사용하도록 하려면 Render Static Site, Vercel 등으로 `frontend`를 별도 배포해야 합니다.

## 구성

```text
chatbot/
├── frontend/                 # React 19 + Vite 8 UI
│   ├── src/
│   │   ├── App.jsx           # 채팅·세션 UI 및 API 호출
│   │   ├── App.css           # 카카오톡 PC 스타일 UI (색상 토큰·레이아웃·말풍선)
│   │   └── main.jsx          # 엔트리포인트
│   ├── .env.example          # 로컬 API 주소 예시
│   ├── .env.production       # 운영 API 주소
│   └── package.json
└── backend/                  # FastAPI API 서버
    ├── main.py               # 라우트, CORS, AI 호출 및 재시도
    ├── db.py                 # SQLite 대화 기록
    ├── requirements.txt
    └── .env.example          # 비밀값 제외 환경 변수 예시
```

## 로컬 실행

### 1. 백엔드

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

`backend/.env`의 `HF_TOKEN=` 뒤에 새 Hugging Face 토큰을 입력한 뒤 서버를 실행합니다.

```powershell
uvicorn main:app --reload --port 8000
```

상태 확인 주소: http://127.0.0.1:8000/health

### 2. 프론트엔드

새 터미널에서 실행합니다.

```powershell
cd frontend
npm install
npm run dev
```

Vite가 표시하는 로컬 주소(기본값은 `http://localhost:5173`)로 접속합니다. 로컬 API 기본 주소는 `http://127.0.0.1:8000`입니다. 다른 로컬 API를 사용하려면 `.env.example`을 `.env.local`로 복사해 `VITE_API_BASE_URL`을 변경합니다.

## 환경 변수

### 백엔드 (`backend/.env` 또는 Render 환경 변수)

| 변수 | 현재 기본값 | 설명 |
| --- | --- | --- |
| `HF_TOKEN` | 없음 | Hugging Face 토큰. 반드시 설정해야 함 |
| `HF_URL` | `https://router.huggingface.co/v1/chat/completions` | AI API 주소 |
| `HF_MODEL` | `Qwen/Qwen3-4B-Instruct-2507` | 호출 모델 |
| `FRONTEND_ORIGINS` | `*` | 허용할 프론트 Origin. 배포 후 공개 프론트 주소로 제한 권장 |
| `AI_REQUEST_TIMEOUT` | `60` | AI 요청 제한 시간(초) |
| `AI_RETRY_ATTEMPTS` | `3` | 일시적 AI 오류 재시도 횟수 |
| `AI_RETRY_DELAY_SECONDS` | `2` | 첫 재시도 전 대기 시간(초) |

### 프론트엔드 (`frontend/.env.*`)

| 파일 | `VITE_API_BASE_URL` |
| --- | --- |
| `.env.example` | `http://127.0.0.1:8000` |
| `.env.production` | `https://chattbot-back.onrender.com` |

## UI 디자인

프론트엔드는 카카오톡 PC 채팅창 분위기의 화면으로 구성되어 있습니다. 기능과 API 연동은 그대로 두고 `frontend/src/App.css`에서 UI만 관리합니다.

- 왼쪽 사이드바: 새 대화 버튼, 대화 목록, 제목 변경·삭제 버튼, 선택 상태
- 오른쪽 채팅창: 블루그레이 배경, 왼쪽 흰색 챗봇 말풍선, 오른쪽 노란색 사용자 말풍선
- 하단 입력 영역: 채팅 내용과 분리되어 항상 표시되며, 메시지 목록만 내부 스크롤됩니다.
- 주요 색상은 CSS 변수로 정의되어 있어 `--kakao-yellow`, `--chat-bg` 등만 조정하면 전체 분위기를 바꿀 수 있습니다.

## API

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| `GET` | `/` | 백엔드 기본 상태 메시지 |
| `GET` | `/health` | Render 상태 확인 (`{"status":"ok"}`) |
| `POST` | `/chat` | 단일 메시지 AI 응답 |
| `POST` | `/sessions` | 새 대화 세션 생성 |
| `GET` | `/sessions` | 세션 목록 조회 |
| `GET` | `/sessions/{session_id}/messages` | 세션 메시지 조회 |
| `POST` | `/sessions/{session_id}/messages` | 메시지 전송 및 AI 응답 저장 |
| `PUT` | `/sessions/{session_id}` | 세션 제목 변경 |
| `DELETE` | `/sessions/{session_id}` | 세션 삭제 |

`POST /chat` 요청 예시:

```json
{ "text": "안녕하세요!" }
```

## 프론트엔드 배포 (Render Static Site)

프론트 공개 주소가 필요할 때 Render에서 Static Site를 생성하고 아래 값을 사용합니다.

| 설정 | 값 |
| --- | --- |
| Repository | `byunhyein/chattbot` |
| Root Directory | `frontend` |
| Build Command | `npm install && npm run build` |
| Publish Directory | `dist` |
| Environment Variable | `VITE_API_BASE_URL=https://chattbot-back.onrender.com` |

배포 후 생성된 프론트 URL을 백엔드 Render의 `FRONTEND_ORIGINS`에 설정합니다.

## 보안 메모

- `backend/.env`와 `backend/chat.db`는 Git에서 제외됩니다.
- Hugging Face 토큰은 코드, README, Git 커밋에 넣지 않습니다.
- 기존 토큰이 노출되었을 가능성이 있다면 Hugging Face에서 폐기하고 새 토큰을 발급합니다.
