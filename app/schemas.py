from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# --- Auth Schemas ---

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters long")

class UserOut(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None


# --- Log Schemas ---

class LogBase(BaseModel):
    service: str = Field(..., min_length=1, max_length=100)
    level: str = Field(..., description="Level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    message: str

class LogCreate(LogBase):
    pass

class LogOut(LogBase):
    id: int
    timestamp: datetime
    user_id: int

    model_config = ConfigDict(from_attributes=True)


# --- Alert Rule Schemas ---

class AlertRuleBase(BaseModel):
    service: str = Field(..., min_length=1, max_length=100)
    threshold: int = Field(..., gt=0, description="Error threshold count to trigger alert")
    window_minutes: int = Field(..., gt=0, description="Sliding window in minutes")
    notify_email: EmailStr = Field(..., description="Email address for notifications")
    notify_webhook_url: Optional[str] = Field(None, description="Optional webhook endpoint (POST)")

class AlertRuleCreate(AlertRuleBase):
    pass

class AlertRuleOut(AlertRuleBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Alert History Schemas ---

class AlertHistoryOut(BaseModel):
    id: int
    service: str
    error_count: int
    threshold: int
    triggered_at: datetime
    notified_email: str

    model_config = ConfigDict(from_attributes=True)


# --- Stats Schemas ---

class ServiceStatItem(BaseModel):
    service: str
    hour: datetime
    error_count: int

    model_config = ConfigDict(from_attributes=True)
