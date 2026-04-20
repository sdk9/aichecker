"""
Admin router — /api/admin/*
All endpoints require is_admin=True on the User model.
"""
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.routers.auth import _get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])

ADMIN_EMAILS = set(
    e.strip() for e in os.getenv("ADMIN_EMAILS", "iacob.zamfir@gmail.com").split(",") if e.strip()
)


def _require_admin(current_user: User = Depends(_get_current_user)) -> User:
    if current_user.email not in ADMIN_EMAILS and not getattr(current_user, "is_admin", False):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    return current_user


# ── Overview stats ────────────────────────────────────────────────────────────

@router.get("/stats")
def get_stats(db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    free_users = db.query(func.count(User.id)).filter(User.plan == "free").scalar()
    pro_users = db.query(func.count(User.id)).filter(User.plan == "pro").scalar()
    enterprise_users = db.query(func.count(User.id)).filter(User.plan == "enterprise").scalar()

    total_scans = db.query(func.sum(User.daily_scans)).scalar() or 0

    this_month = datetime.now(timezone.utc).strftime("%Y-%m")
    scans_this_month = (
        db.query(func.sum(User.daily_scans))
        .filter(User.last_scan_date == this_month)
        .scalar() or 0
    )

    # New users last 30 days
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    new_users_30d = db.query(func.count(User.id)).filter(User.created_at >= cutoff).scalar()

    # New users last 7 days
    cutoff7 = datetime.now(timezone.utc) - timedelta(days=7)
    new_users_7d = db.query(func.count(User.id)).filter(User.created_at >= cutoff7).scalar()

    # Users with stripe customer (ever attempted upgrade)
    stripe_users = (
        db.query(func.count(User.id)).filter(User.stripe_customer_id != None).scalar()
    )

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users,
            "free": free_users,
            "pro": pro_users,
            "enterprise": enterprise_users,
            "new_last_7d": new_users_7d,
            "new_last_30d": new_users_30d,
            "with_stripe": stripe_users,
        },
        "scans": {
            "total_all_time": total_scans,
            "this_month": scans_this_month,
        },
        "revenue": {
            "monthly_mrr_cents": pro_users * 499 + enterprise_users * 0,
            "monthly_mrr_usd": round((pro_users * 499) / 100, 2),
        },
    }


# ── User list ─────────────────────────────────────────────────────────────────

@router.get("/users")
def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    plan: Optional[str] = Query(None),
    sort: str = Query("created_at"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
    _: User = Depends(_require_admin),
):
    q = db.query(User)

    if search:
        term = f"%{search}%"
        q = q.filter((User.email.like(term)) | (User.full_name.like(term)))

    if plan:
        q = q.filter(User.plan == plan)

    total = q.count()

    sort_col = getattr(User, sort, User.created_at)
    if order == "desc":
        q = q.order_by(sort_col.desc())
    else:
        q = q.order_by(sort_col.asc())

    users = q.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
        "users": [_user_row(u) for u in users],
    }


# ── Single user ───────────────────────────────────────────────────────────────

@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return _user_row(user, full=True)


@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    body: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(_require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    allowed = {"plan", "is_active", "full_name"}
    for key, val in body.items():
        if key in allowed:
            setattr(user, key, val)

    db.commit()
    db.refresh(user)
    logger.info("Admin %s updated user %s: %s", admin.email, user.email, body)
    return _user_row(user, full=True)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(_require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    if user.email in ADMIN_EMAILS:
        raise HTTPException(400, "Cannot delete an admin account")
    db.delete(user)
    db.commit()
    logger.info("Admin %s deleted user %s", admin.email, user.email)
    return {"deleted": True}


# ── Recent activity ───────────────────────────────────────────────────────────

@router.get("/activity")
def recent_activity(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(_require_admin),
):
    recent = (
        db.query(User)
        .filter(User.last_scan_date != None)
        .order_by(User.updated_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "user_id": u.id,
            "email": u.email,
            "plan": u.plan,
            "scans": u.daily_scans,
            "last_active": u.updated_at.isoformat() if u.updated_at else None,
        }
        for u in recent
    ]


# ── Plan breakdown (for chart) ────────────────────────────────────────────────

@router.get("/plans/breakdown")
def plan_breakdown(db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    rows = db.query(User.plan, func.count(User.id)).group_by(User.plan).all()
    return [{"plan": r[0], "count": r[1]} for r in rows]


@router.get("/signups/daily")
def signups_daily(
    days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db),
    _: User = Depends(_require_admin),
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    users = db.query(User).filter(User.created_at >= cutoff).all()

    buckets: dict[str, int] = {}
    for u in users:
        day = u.created_at.strftime("%Y-%m-%d") if u.created_at else "unknown"
        buckets[day] = buckets.get(day, 0) + 1

    sorted_days = sorted(buckets.items())
    return [{"date": d, "signups": c} for d, c in sorted_days]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _user_row(u: User, full: bool = False) -> dict:
    row = {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "plan": u.plan,
        "is_active": u.is_active,
        "is_verified": u.is_verified,
        "daily_scans": u.daily_scans,
        "last_scan_date": u.last_scan_date,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }
    if full:
        row.update({
            "stripe_customer_id": u.stripe_customer_id,
            "stripe_subscription_id": u.stripe_subscription_id,
            "updated_at": u.updated_at.isoformat() if u.updated_at else None,
        })
    return row
