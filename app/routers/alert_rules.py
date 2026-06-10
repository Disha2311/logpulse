from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.dependencies import get_db, get_current_user
from app.models import User, AlertRule
from app.schemas import AlertRuleCreate, AlertRuleOut

router = APIRouter(prefix="/alert-rules", tags=["alert-rules"])

@router.post("", response_model=AlertRuleOut, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    rule_in: AlertRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new alert rule for a service."""
    # Check if a rule for the service already exists (optional, but let's allow multiple or check)
    result = await db.execute(select(AlertRule).where(
        (AlertRule.service == rule_in.service) & 
        (AlertRule.notify_email == rule_in.notify_email)
    ))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An alert rule for service '{rule_in.service}' notifying '{rule_in.notify_email}' already exists."
        )

    db_rule = AlertRule(
        service=rule_in.service,
        threshold=rule_in.threshold,
        window_minutes=rule_in.window_minutes,
        notify_email=rule_in.notify_email,
        notify_webhook_url=rule_in.notify_webhook_url
    )
    db.add(db_rule)
    await db.commit()
    await db.refresh(db_rule)
    return db_rule

@router.get("", response_model=List[AlertRuleOut])
async def list_alert_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all alert rules."""
    result = await db.execute(select(AlertRule).order_by(AlertRule.created_at.desc()))
    return result.scalars().all()

@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an alert rule."""
    result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
    db_rule = result.scalars().first()
    if not db_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )
    
    await db.delete(db_rule)
    await db.commit()
    return None
