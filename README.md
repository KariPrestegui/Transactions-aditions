# Python - React

A project integrating a FastAPI backend with a React frontend, demonstrating database interactions, asynchronous processing with Celery, real-time updates via WebSockets, and AI integration using OpenAI's API. The project also includes an RPA script using Playwright to automate web interactions.

## Architecture

```
                    ┌─────────────┐
                    │   Frontend  │
                    │ React+Vite  │
                    └──────┬──────┘
                           │ HTTP / WebSocket
                    ┌──────▼──────┐
                    │   Backend   │
                    │   FastAPI   │
                    └──┬───┬───┬──┘
               ┌───────┘   │   └───────┐
        ┌──────▼──┐  ┌─────▼────┐ ┌────▼─────┐
        │PostgreSQL│  │  Redis   │ │  OpenAI  │
        │   DB     │  │  Queue   │ │   API    │
        └─────────┘  └─────┬────┘ └──────────┘
                     ┌──────▼──────┐
                     │   Celery    │
                     │   Worker    │
                     └─────────────┘
```

## Prerequisites

```

| Service    | URL                              |
| ---------- | -------------------------------- |
| Frontend   | http://localhost:3000             |
| Backend    | http://localhost:8000             |
| API Docs   | http://localhost:8000/docs        |
| PostgreSQL | localhost:5432                    |
| Redis      | localhost:6379                    |

## Local Development

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

# Start PostgreSQL and Redis locally, then:
uvicorn app.main:app --reload --port 8000
```

### Celery Worker

```bash
cd backend
celery -A app.workers.celery_worker worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### RPA Script

```bash
cd rpa
pip install -r requirements.txt
playwright install chromium

python wikipedia_bot.py "Python programming"
```

## API Endpoints

### Health Check

```
GET /health
```

### Create Transaction (sync)

```
POST /transactions/create
Content-Type: application/json

{
  "user_id": "user-123",
  "amount": 150.75,
  "type": "deposit"
}
```

### Create Transaction (async with Celery)

```
POST /transactions/async-process
Content-Type: application/json

{
  "user_id": "user-456",
  "amount": 500.00,
  "type": "withdrawal"
}
```

**Response (202 Accepted):**

```json
{
  "transaction_id": "uuid",
  "status": "pending",
  "task_id": "celery-task-id",
  "message": "Transaction queued for processing"
}
```

### List Transactions

```
GET /transactions/
```

### WebSocket Stream

```
WS ws://localhost:8000/transactions/stream
```

Messages received:

```json
{
  "event": "transaction_update",
  "transaction_id": "uuid",
  "status": "processed",
  "timestamp": "2026-03-06T21:00:00Z"
}
```

### AI Summarization

```
POST /assistant/summarize
Content-Type: application/json

{
  "text": "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by animals including humans..."
}
```

**Response:**

```json
{
  "summary": "...",
  "model_used": "gpt-3.5-turbo",
  "request_id": "uuid"
}
```

> **Note:** If `OPENAI_API_KEY` is not set, the API returns a simulated summary.

## Environment Variables

| Variable         | Default                                          | Description                  |
| ---------------- | ------------------------------------------------ | ---------------------------- |
| `DATABASE_URL`   | `postgresql://postgres:postgres@postgres:5432/fullstack_db` | PostgreSQL connection string |
| `REDIS_URL`      | `redis://redis:6379/0`                           | Redis broker URL             |
| `OPENAI_API_KEY` | _(empty)_                                        | OpenAI API key (optional)    |
| `VITE_API_URL`   | `http://localhost:8000`                           | Backend URL for frontend     |
| `VITE_WS_URL`    | `ws://localhost:8000`                             | WebSocket URL for frontend   |

## Tech Stack

| Layer          | Technology                     |
| -------------- | ------------------------------ |
| Backend        | FastAPI, SQLAlchemy, Alembic   |
| Database       | PostgreSQL 16                  |
| Queue/Cache    | Redis 7 + Celery 5             |
| Real-time      | WebSocket (native FastAPI)     |
| AI Integration | OpenAI GPT-3.5 Turbo           |
| Frontend       | React 18 + Vite 5              |
| RPA            | Playwright (Python)            |       
