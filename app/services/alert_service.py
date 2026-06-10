from datetime import datetime, timedelta, timezone
from typing import List
import redis
import redis.asyncio as aioredis
from app.config import settings

# Clients
redis_async = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
redis_sync = redis.from_url(settings.REDIS_URL, decode_responses=True)

class AlertService:
    @staticmethod
    def _get_window_keys(service: str, window_minutes: int, now: datetime) -> List[str]:
        """Generate the Redis keys representing each minute of the window."""
        keys = []
        for i in range(window_minutes):
            minute_time = now - timedelta(minutes=i)
            minute_str = minute_time.strftime("%Y-%m-%d-%H-%M")
            keys.append(f"errors:{service}:{minute_str}")
        return keys

    # --- Async Methods (For FastAPI) ---
    
    @classmethod
    async def track_error(cls, service: str) -> int:
        """Increment error count for service at current minute. Returns the new value."""
        now = datetime.now(timezone.utc)
        minute_str = now.strftime("%Y-%m-%d-%H-%M")
        key = f"errors:{service}:{minute_str}"
        
        # Increment and set TTL if new
        count = await redis_async.incr(key)
        if count == 1:
            await redis_async.expire(key, 600)  # 10 minutes
        return count

    @classmethod
    async def get_error_count_async(cls, service: str, window_minutes: int) -> int:
        """Sum error rates for a service over the last window_minutes asynchronously."""
        now = datetime.now(timezone.utc)
        keys = cls._get_window_keys(service, window_minutes, now)
        values = await redis_async.mget(keys)
        
        total = 0
        for val in values:
            if val is not None:
                total += int(val)
        return total

    # --- Sync Methods (For Celery worker) ---

    @classmethod
    def get_error_count_sync(cls, service: str, window_minutes: int) -> int:
        """Sum error rates for a service over the last window_minutes synchronously."""
        now = datetime.now(timezone.utc)
        keys = cls._get_window_keys(service, window_minutes, now)
        values = redis_sync.mget(keys)
        
        total = 0
        for val in values:
            if val is not None:
                total += int(val)
        return total

    @classmethod
    def is_cooldown_active(cls, service: str) -> bool:
        """Check if an alert cooldown lock is active for the service."""
        cooldown_key = f"alerts:{service}:cooldown"
        return bool(redis_sync.exists(cooldown_key))

    @classmethod
    def set_cooldown(cls, service: str, cooldown_minutes: int = 5) -> None:
        """Set a cooldown lock for the service to prevent rapid alert firing."""
        cooldown_key = f"alerts:{service}:cooldown"
        redis_sync.setex(cooldown_key, cooldown_minutes * 60, "active")
