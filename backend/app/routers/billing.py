"""
Stripe billing router — /api/billing/*
Endpoints: plans, create-checkout, portal, webhook
"""
import logging
import os

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.routers.auth import _get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/billing", tags=["billing"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# ── Plans ─────────────────────────────────────────────────────────────────────
PLANS = [
    {
        "id": "free",
        "name": "Free",
        "price": 0,
        "currency": "usd",
        "interval": None,
        "scans_per_day": 10,
        "features": [
            "10 scans / day",
            "Images, documents, audio",
            "PDF evidence report",
            "Neural network classifiers",
        ],
        "stripe_price_id": None,
        "cta": "Current plan",
    },
    {
        "id": "pro",
        "name": "Pro",
        "price": 1900,  # cents
        "currency": "usd",
        "interval": "month",
        "scans_per_day": 500,
        "features": [
            "500 scans / day",
            "All file types + video",
            "Priority processing",
            "PDF evidence report",
            "Neural network classifiers",
            "API access",
        ],
        "stripe_price_id": os.getenv("STRIPE_PRO_PRICE_ID", ""),
        "cta": "Upgrade to Pro",
    },
    {
        "id": "enterprise",
        "name": "Enterprise",
        "price": 9900,  # cents
        "currency": "usd",
        "interval": "month",
        "scans_per_day": 9999,
        "features": [
            "Unlimited scans",
            "All file types",
            "Bulk API for pipelines",
            "Priority processing",
            "PDF evidence report",
            "Neural network classifiers",
            "Dedicated support",
            "Custom integrations",
        ],
        "stripe_price_id": os.getenv("STRIPE_ENTERPRISE_PRICE_ID", ""),
        "cta": "Contact Sales",
    },
]


# ── Schemas ───────────────────────────────────────────────────────────────────

class CheckoutRequest(BaseModel):
    plan_id: str  # "pro" | "enterprise"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/plans")
def get_plans():
    """Return plan definitions (no auth required)."""
    return {"plans": PLANS}


@router.post("/create-checkout")
def create_checkout(
    body: CheckoutRequest,
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
):
    """Create a Stripe Checkout Session for the given plan."""
    if not stripe.api_key:
        raise HTTPException(503, "Payments not configured on this server")

    plan = next((p for p in PLANS if p["id"] == body.plan_id), None)
    if not plan or not plan["stripe_price_id"]:
        raise HTTPException(400, "Invalid plan or plan not purchasable")

    # Get or create Stripe customer
    customer_id = current_user.stripe_customer_id
    if not customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.full_name or current_user.email,
            metadata={"user_id": str(current_user.id)},
        )
        customer_id = customer.id
        current_user.stripe_customer_id = customer_id
        db.commit()

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{"price": plan["stripe_price_id"], "quantity": 1}],
        success_url=f"{FRONTEND_URL}/account?upgrade=success",
        cancel_url=f"{FRONTEND_URL}/pricing?upgrade=cancelled",
        metadata={"user_id": str(current_user.id), "plan_id": body.plan_id},
    )
    return {"url": session.url}


@router.post("/portal")
def customer_portal(
    current_user: User = Depends(_get_current_user),
):
    """Return a Stripe Customer Portal URL for subscription management."""
    if not stripe.api_key:
        raise HTTPException(503, "Payments not configured on this server")
    if not current_user.stripe_customer_id:
        raise HTTPException(400, "No billing account found")

    session = stripe.billing_portal.Session.create(
        customer=current_user.stripe_customer_id,
        return_url=f"{FRONTEND_URL}/account",
    )
    return {"url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """Handle Stripe webhook events."""
    if not WEBHOOK_SECRET:
        raise HTTPException(503, "Webhook not configured")

    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid webhook signature")

    db = next(get_db())
    try:
        _handle_event(event, db)
    finally:
        db.close()

    return {"received": True}


def _handle_event(event: dict, db: Session):
    etype = event["type"]

    if etype in ("customer.subscription.created", "customer.subscription.updated"):
        sub = event["data"]["object"]
        _update_subscription(sub, db)

    elif etype == "customer.subscription.deleted":
        sub = event["data"]["object"]
        user = db.query(User).filter(User.stripe_customer_id == sub["customer"]).first()
        if user:
            user.plan = "free"
            user.stripe_subscription_id = None
            db.commit()
            logger.info("Subscription cancelled for user %s", user.email)

    elif etype == "checkout.session.completed":
        session = event["data"]["object"]
        if session.get("subscription"):
            sub = stripe.Subscription.retrieve(session["subscription"])
            _update_subscription(sub, db)

    else:
        logger.debug("Unhandled Stripe event: %s", etype)


def _update_subscription(sub: dict, db: Session):
    customer_id = sub["customer"]
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if not user:
        logger.warning("No user found for Stripe customer %s", customer_id)
        return

    # Determine plan from price metadata or price ID matching
    plan_id = "free"
    if sub.get("items", {}).get("data"):
        price_id = sub["items"]["data"][0]["price"]["id"]
        for plan in PLANS:
            if plan.get("stripe_price_id") == price_id:
                plan_id = plan["id"]
                break

    status = sub.get("status", "")
    if status in ("active", "trialing"):
        user.plan = plan_id
    else:
        user.plan = "free"

    user.stripe_subscription_id = sub["id"]
    db.commit()
    logger.info("Updated plan for user %s → %s (status: %s)", user.email, user.plan, status)
