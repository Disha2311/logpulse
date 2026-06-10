# ⚡ LogFlow | Real-Time Log Aggregator and Alerting System

**LogFlow** is a full-stack portfolio project demonstrating a real-time log ingestion, processing, alerting, and visualization dashboard. Applications stream logs to this system via a REST API. The system stores logs in PostgreSQL, tracks error rates in real time using sliding windows in Redis, dispatches automated alerts when thresholds are breached, and broadcasts log activity to a React dashboard over WebSockets.

---

## 🏛️ System Architecture

```text
               +----------------------------------------+
               |          Clients / Applications        |
               +----------------------------------------+
                                   | Ingests logs (REST)
                                   v
+-----------------------------------------------------------------------+
|  BACKEND (FastAPI API Node)                                           |
|                                                                       |
|   +--------------+      +------------------+      +----------------+  |
|   |  Auth Router |      |   Logs Ingestor  |      | Alert Rules API|  |
|   +--------------+      +------------------+      +----------------+  |
|          |                       |                        |           |
|          | Queries credentials   | Save Logs              | Rule CRUD |
|          v                       v                        v           |
|    +------------+          +------------+          +------------+     |
|    | PostgreSQL |<---------| PostgreSQL |          | PostgreSQL |     |
|    |   (User)   |          |   (Logs)   |          |  (Rules)   |     |
|    +------------+          +------------+          +------------+     |
|                                  | If ERROR/CRITICAL                  |
|                                  v                                    |
|                            +------------+                             |
|                            |   Redis    |                             |
|                            |  Counters  |                             |
|                            +------------+                             |
|                                  ^                                    |
|                                  | Fetch Rates & Cooldown Locks       |
|                                  v                                    |
|   +--------------+      +------------------+      +----------------+  |
|   | Celery Beat  |----->|  Celery Workers  |----->| Alerts Service |  |
|   | (Schedulers) | 60s  | (Alert Checkers) |      | (SMTP/Webhooks)|  |
|   +--------------+      +------------------+      +----------------+  |
|                                                           |           |
|                                                           v           |
|                                                   +----------------+  |
|                                                   |  Alert History |  |
|                                                   +----------------+  |
+-----------------------------------------------------------------------+
        | Broadcasts logs (WebSocket stream)
        v
+-----------------------------------------------------------------------+
|  FRONTEND (React 18 Dashboard)                                        |
|                                                                       |
|   +-----------------------+   +-------------------+   +------------+  |
|   |  Service Health Cards |   | Error Rates Chart |   | Live Feed  |  |
|   |  (Green/Yellow/Red)   |   |    (Recharts)     |   | (WebSocket)|  |
|   +-----------------------+   +-------------------+   +------------+  |
+-----------------------------------------------------------------------+
```

---

## 🚀 Key Features

* **Asynchronous Log Ingestion:** Fast, non-blocking log ingestion endpoints using async FastAPI, asyncpg, and SQLAlchemy 2.0.
* **Sliding Window Error Rate Tracking:** Redis cache tracks error rates per service using minute-level keys (e.g. `errors:{service}:{YYYY-MM-DD-HH-MM}`) with 10-minute auto-expiry, avoiding heavy DB queries.
* **Distributed Alert Scheduler:** Celery worker and Celery Beat scheduler executing automated checks every 60 seconds against Redis metrics.
* **Multi-Channel Alert Dispatcher:** Supports sending HTML/Plain-text SMTP emails and delivering JSON payloads to webhook POST targets (e.g. Slack/Teams).
* **Alert Cooldown Locks:** Implements a 5-minute Redis-based cooling period (`alerts:{service}:cooldown`) to prevent duplicate alert notifications.
* **Live WebSocket Broadcasts:** Stream raw logs from endpoints directly to browser clients with JWT authentication.
* **Premium Glassmorphic Dashboard:** Implemented a dark mode dashboard featuring:
  - **Service Health status cards** that change color dynamically (Green/Yellow/Red) by matching recent errors against active rule thresholds.
  - **Interactive Line charts** using Recharts showing error volumes over the last 24 hours.
  - **Advanced Log Finder** filtering logs by Level, Service, and Date-Time ranges with pagination support.

---

## 📂 Project Structure

```text
log-aggregator/
├── app/
│   ├── main.py                  ← FastAPI app init, router registration
│   ├── database.py              ← Async SQLAlchemy engine and session
│   ├── models.py                ← SQLAlchemy database models
│   ├── schemas.py               ← Pydantic schemas (validation/serialization)
│   ├── dependencies.py          ← Reusable dependencies (get_db, auth checks)
│   ├── websocket_manager.py     ← Real-time socket broadcast manager
│   ├── routers/                 ← API controllers (auth, logs, alert rules, stats)
│   ├── services/                ← Business logic (logs, Redis tracking, SMTP, Webhooks)
│   └── workers/                 ← Celery worker and scheduler task definitions
├── frontend/
│   ├── index.html               ← Main entry HTML with viewport and SEO meta
│   ├── vite.config.js           ← Dev server configured to serve port 3000
│   └── src/                     
│       ├── api/axios.js         ← Axios client with memory JWT interceptors
│       ├── pages/               ← Login / Register and Dashboard controllers
│       ├── components/          ← Health cards, Recharts, tables, and WebSockets
│       └── index.css            ← CSS HSL Design system and utility classes
├── tests/                       ← Pytest unit and integration test suite
├── docker-compose.yml           ← Full multi-container orchestrator
├── Dockerfile                   ← Multi-stage production Dockerfile
└── send_mock_logs.py            ← REST Ingestion simulator
```

---

## 🛠️ Quickstart Guide

### Option 1: Docker Compose (Recommended Setup)
To run the entire ecosystem (PostgreSQL, Redis, FastAPI, Celery, and Beat) with a single command:
```bash
docker-compose up --build
```
This command automatically:
1. Spins up PostgreSQL and Redis.
2. Applies Alembic database migrations.
3. Launches the FastAPI app (port `8000`), Celery worker, and Celery beat scheduler.

Then, start the frontend client:
```bash
cd frontend
npm install
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

---

### Option 2: Local Run (Zero-Setup SQLite Mode)
If you do not have Docker or PostgreSQL running locally, the project has an **automatic SQLite fallback** for out-of-the-box local development.

1. **Setup Backend Environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   
   pip install -r requirements.txt
   ```
2. **Start FastAPI Development Server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   *Note: On launch, the database file `logflow.db` will be created and all schemas initialized automatically.*

3. **Start React Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Start Ingestion Simulator:**
   To populate your dashboard and test alerting policies, run our simulator script:
   ```bash
   python send_mock_logs.py
   ```

---

## 🧪 Running Automated Tests

To execute the test suite (13 unit and integration tests verifying authentication, log filters, stats aggregations, Celery alerting logic, and Redis cooldowns):
```bash
python -m pytest -v
```

---

## 🔌 API Endpoints Reference

### Authentication
* `POST /auth/register` - Creates a new user profile (`{email, password}`).
* `POST /auth/login` - Authenticates user and returns JWT access token.

### Log Management
* `POST /logs` - Ingests a new log entry. Requires JWT header. If ERROR/CRITICAL, increments Redis counters.
* `GET /logs` - Fetch logs from DB. Supports query filtering: `level`, `service`, `date_from`, `date_to`, `page`, and `limit`.
* `GET /logs/stats` - Fetch hourly error frequencies grouped by service over the last 24 hours.

### Alerting Rules & Logs
* `POST /alert-rules` - Creates a service alerting rule (`{service, threshold, window_minutes, notify_email, notify_webhook_url}`).
* `GET /alert-rules` - Lists active rule policies.
* `DELETE /alert-rules/{id}` - Deletes a rule policy.
* `GET /alert-history` - Lists triggered alerts with optional service filter.

### WebSocket
* `WS /ws/logs?token=<JWT>` - Receives live log broadcasts.
