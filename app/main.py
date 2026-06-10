from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt

from app.config import settings
from app.database import engine, Base
from app.websocket_manager import manager
from app.routers import auth, logs, alert_rules, stats

app = FastAPI(
    title="Real-Time Log Aggregator and Alerting System",
    description="FastAPI backend for ingesting logs, managing alert rules, tracking metrics, and broadcasting log updates.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Create tables on startup if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# CORS configuration
# Allow local React dashboard (localhost:3000) and headers for JWT auth
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(logs.router)
app.include_router(alert_rules.router)
app.include_router(stats.router)

@app.get("/health", tags=["system"])
async def health_check():
    """System health check endpoint."""
    return {"status": "healthy"}

@app.websocket("/ws/logs")
async def websocket_logs_endpoint(websocket: WebSocket, token: Optional[str] = None):
    """
    WebSocket feed broadcasting live logs to connected clients in real time.
    Requires authentication via token query parameter (e.g. /ws/logs?token=<JWT>).
    """
    if not token:
        token = websocket.query_params.get("token")
        
    if not token:
        # Policy violation close code
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
        
    try:
        # Verify JWT Token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Connection accepted and registered
    await manager.connect(websocket)
    try:
        while True:
            # Block and keep connection open, handle any incoming control frames
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
