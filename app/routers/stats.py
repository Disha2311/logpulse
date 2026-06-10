from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.dependencies import get_db, get_current_user
from app.models import User, AlertHistory
from app.schemas import ServiceStatItem, AlertHistoryOut
from app.services.log_service import LogService

router = APIRouter(tags=["stats"])

@router.get("/logs/stats", response_model=List[ServiceStatItem])
async def get_log_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve error metrics per service grouped by hour for the last 24 hours."""
    stats = await LogService.get_error_stats_24h(db)
    return stats

@router.get("/alert-history", response_model=List[AlertHistoryOut])
async def get_alert_history(
    service: Optional[str] = Query(None, description="Filter alert history by service name"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve past triggered alerts, sorted by triggered_at descending."""
    query = select(AlertHistory)
    if service:
        query = query.where(AlertHistory.service == service)
        
    query = query.order_by(AlertHistory.triggered_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()
