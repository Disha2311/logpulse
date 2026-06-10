from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.models import User
from app.schemas import LogCreate, LogOut
from app.services.log_service import LogService
from app.services.alert_service import AlertService
from app.websocket_manager import manager

router = APIRouter(prefix="/logs", tags=["logs"])

@router.post("", response_model=LogOut, status_code=status.HTTP_201_CREATED)
async def ingest_log(
    log_in: LogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ingest a log, increment Redis error counters (if ERROR/CRITICAL), and stream via WebSocket."""
    # Save to PostgreSQL
    db_log = await LogService.create_log(db, log_in, current_user.id)
    
    # Increment Redis counter if level is ERROR or CRITICAL
    if db_log.level in ["ERROR", "CRITICAL"]:
        await AlertService.track_error(db_log.service)
        
    # Broadcast to WebSocket subscribers
    log_out = LogOut.model_validate(db_log)
    await manager.broadcast(log_out.model_dump(mode="json"))
    
    return db_log

@router.get("", response_model=List[LogOut])
async def fetch_logs(
    level: Optional[str] = Query(None, description="Filter by log level (DEBUG, INFO, etc.)"),
    service: Optional[str] = Query(None, description="Filter by service name"),
    date_from: Optional[datetime] = Query(None, description="Filter from timestamp (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="Filter to timestamp (ISO format)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve logs with filters and pagination."""
    logs = await LogService.get_logs(
        db=db,
        level=level,
        service=service,
        date_from=date_from,
        date_to=date_to,
        page=page,
        limit=limit
    )
    return logs
