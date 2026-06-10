from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
import bcrypt
from app.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against its hash using bcrypt directly."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Generate password hash from plain text using bcrypt directly."""
    # Bcrypt requires bytes
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a JWT token signed with SECRET_KEY."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": int(expire.timestamp())})
    # Set the subject as string
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
        
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
