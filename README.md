# Deviation Intake Module — AIVOA AI Product Engineer Challenge

Workflow: **Deviation document/text → AI extraction → Log Deviation form → AI impact & severity → user review → save.**

## Stack
- Frontend: React (Vite) + Redux Toolkit — `frontend/`
- Backend: Python + FastAPI — `backend/app/`
- AI: LangGraph + Groq (`llama-3.3-70b-versatile` default, `gemma2-9b-it` also works) with heuristic fallback when no key is set
- DB: PostgreSQL (docker) or SQLite for quick local run

## Quick start

Backend:
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows | source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
copy .env.example .env        # then edit GROQ_API_KEY
set DATABASE_URL=sqlite:///./deviations.db
uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173
```

Health check: `curl http://localhost:8000/health`

## With Postgres (docker)
```bash
docker compose up --build
# backend http://localhost:8000, db on :5432
# set DATABASE_URL=postgresql+psycopg2://deviation:deviation@localhost:5432/deviations
```

## Demo script (5–8 min video)
1. Show empty Log Deviation form + empty logged list (0:00–0:30).
2. AI panel → Load sample (or paste `sample-documents/deviation-email-01.txt`, or upload it) → Analyze with AI (0:30–2:00). Point out LangGraph nodes `extract → assess` in `backend/app/services/ai_graph.py`.
3. Show severity badge (Major), impact text, reason + confidence → Apply to form (2:00–3:30).
4. Review/edit left form (change severity if you disagree — human-in-the-loop) → Save → show `DEV-2026-0001` + row in Logged deviations table (3:30–5:00).
5. Code walkthrough: frontend slice (`deviationSlice.js`), `POST /api/ai/analyze`, LangGraph graph, `POST /api/deviations`, Postgres/SQLite model (5:00–7:30).

## API
- `POST /api/ai/analyze` `{text}` → `{extracted, severity, impact_assessment, ai_reason, ai_confidence, provider}`
- `POST /api/ai/analyze-file` multipart (txt/pdf) → same
- `GET /api/deviations` → list
- `POST /api/deviations` → save (requires title)
- `GET /health` → groq configured? model?

