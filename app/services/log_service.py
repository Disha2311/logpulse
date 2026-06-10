from datetime import datetime, timedelta, timezone
from typing import Optional, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Log
from app.schemas import LogCreate

class LogService:
    @staticmethod
    async def create_log(db: AsyncSession, log_in: LogCreate, user_id: int) -> Log:
        """Create a new log entry in the database."""
        db_log = Log(
            service=log_in.service,
            level=log_in.level.upper(),
            message=log_in.message,
            user_id=user_id
        )
        db.add(db_log)
        await db.commit()
        await db.refresh(db_log)
        return db_log

    @staticmethod
    async def get_logs(
        db: AsyncSession,
        level: Optional[str] = None,
        service: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        page: int = 1,
        limit: int = 50
    ) -> List[Log]:
        """Fetch logs from the database with optional filtering and pagination."""
        query = select(Log)
        
        filters = []
        if level:
            filters.append(Log.level == level.upper())
        if service:
            filters.append(Log.service == service)
        if date_from:
            filters.append(Log.timestamp >= date_from)
        if date_to:
            filters.append(Log.timestamp <= date_to)
            
        if filters:
            query = query.where(and_(*filters))
            
        # Order by newest first
        query = query.order_by(Log.timestamp.desc())
        
        # Pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_error_stats_24h(db: AsyncSession) -> List[dict]:
        """
        Get error/critical count per service grouped by hour for the last 24 hours.
        Returns a list of dicts with keys: service, hour, error_count.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        
        # Dialect-aware grouping for testing (SQLite vs PostgreSQL)
        dialect_name = db.bind.dialect.name
        if dialect_name == "sqlite":
            hour_expr = func.strftime("%Y-%m-%dT%H:00:00.000Z", Log.timestamp)
        else:
            # PostgreSQL: date_trunc returns datetime, we select it
            hour_expr = func.date_trunc("hour", Log.timestamp)
            
        query = (
            select(
                Log.service,
                hour_expr.label("hour"),
                func.count(Log.id).label("error_count")
            )
            .where(
                and_(
                    Log.level.in_(["ERROR", "CRITICAL"]),
                    Log.timestamp >= cutoff
                )
            )
            .group_by(Log.service, "hour")
            .order_by("hour")
        )
        
        result = await db.execute(query)
        stats = []
        for row in result.all():
            hour_val = row.hour
            # If hour_val is a string from SQLite, parse or leave as ISO string,
            # otherwise if datetime (PostgreSQL), make it timezone aware or parse it.
            if isinstance(hour_val, str):
                try:
                    # Parse sqlite strftime
                    hour_dt = datetime.fromisoformat(hour_val.replace("Z", "+00:00"))
                except ValueError:
                    hour_dt = datetime.strptime(hour_val, "%Y-%m-%d %H:00:00")
            else:
                hour_dt = hour_val
                
            stats.append({
                "service": row.service,
                "hour": hour_dt,
                "error_count": row.error_count
            })
        return stats
