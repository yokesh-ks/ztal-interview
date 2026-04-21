# Running The Assignment App

This repo contains:

- a minimal runnable frontend app
- a minimal runnable backend API
- an intentionally incomplete chatbot feature
- existing product tradeoffs and architectural constraints for the interview process
- fuller standards reference docs

## Backend

From `backend/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn recruitment_agent.server.app:app --reload
```

The backend runs at:

- `http://127.0.0.1:8000`

## Frontend

From `frontend/`:

```bash
npm install
npm run dev
```

The frontend runs at:

- `http://127.0.0.1:5173`

By default it expects the backend chat endpoint at:

- `http://127.0.0.1:8000/api/chat/reply`

You can override this with:

```bash
VITE_CHAT_ENDPOINT=http://127.0.0.1:8000/api/chat/reply npm run dev
```
