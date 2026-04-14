"""
Auth router — /api/auth/*
Endpoints: register, login, me, forgot-password, reset-password
"""
import os
import secrets
import smtplib
import logging
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.auth import create_access_token, decode_token, hash_password, verify_password
from app.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])
bearer = HTTPBearer(auto_error=False)

# ── Plan limits ───────────────────────────────────────────────────────────────
PLAN_DAILY_LIMITS = {"free": 10, "pro": 500, "enterprise": 9999}


# ── Schemas ───────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    plan: str
    is_verified: bool
    daily_scans: int
    daily_limit: int
    created_at: str

    model_config = {"from_attributes": True}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user


def _send_reset_email(to_email: str, token: str):
    """Send password reset email. Falls back to console log if SMTP not configured."""
    reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/reset-password?token={token}"
    subject = "VeritasAI — Reset your password"
    body = (
        f"Hi,\n\n"
        f"You requested a password reset for your VeritasAI account.\n\n"
        f"Click this link to reset your password (valid for 1 hour):\n{reset_url}\n\n"
        f"If you didn't request this, ignore this email.\n\n"
        f"— VeritasAI Team"
    )

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_from = os.getenv("SMTP_FROM", smtp_user or "noreply@veritasai.app")

    if smtp_host and smtp_user and smtp_pass:
        try:
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = smtp_from
            msg["To"] = to_email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_from, [to_email], msg.as_string())
            logger.info("Password reset email sent to %s", to_email)
        except Exception as exc:
            logger.warning("Failed to send reset email: %s", exc)
            logger.info("PASSWORD RESET TOKEN for %s: %s", to_email, token)
            logger.info("Reset URL: %s", reset_url)
    else:
        # No SMTP configured — log to console (useful in dev / VPS without mail server)
        logger.info("=" * 60)
        logger.info("PASSWORD RESET TOKEN for %s", to_email)
        logger.info("Reset URL: %s", reset_url)
        logger.info("=" * 60)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register", status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(400, "Email already registered")
    if len(body.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")

    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
        is_verified=True,  # skip email verification for now
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer", "user": _user_out(user)}


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(401, "Invalid email or password")
    if not user.is_active:
        raise HTTPException(403, "Account disabled")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer", "user": _user_out(user)}


@router.get("/me")
def me(current_user: User = Depends(_get_current_user)):
    return _user_out(current_user)


@router.post("/forgot-password")
def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    # Always return 200 to avoid user enumeration
    if user:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
        db.commit()
        _send_reset_email(user.email, token)
    return {"message": "If that email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    if len(body.new_password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    user = db.query(User).filter(User.reset_token == body.token).first()
    if not user:
        raise HTTPException(400, "Invalid or expired reset token")
    if user.reset_token_expiry and datetime.now(timezone.utc) > user.reset_token_expiry.replace(tzinfo=timezone.utc):
        raise HTTPException(400, "Reset token has expired")

    user.hashed_password = hash_password(body.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()
    return {"message": "Password updated successfully"}


# ── Utility ───────────────────────────────────────────────────────────────────

def _user_out(user: User) -> dict:
    limit = PLAN_DAILY_LIMITS.get(user.plan, 10)
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "plan": user.plan,
        "is_verified": user.is_verified,
        "daily_scans": user.daily_scans,
        "daily_limit": limit,
        "created_at": user.created_at.isoformat() if user.created_at else "",
    }


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Returns current user if authenticated, None otherwise (for optional auth)."""
    if not credentials:
        return None
    payload = decode_token(credentials.credentials)
    if not payload:
        return None
    return db.query(User).filter(User.email == payload.get("sub")).first()
