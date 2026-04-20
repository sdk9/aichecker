"""
VeritasAI — AI Content Detection API
FastAPI application entry point.
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.analyze import router as analyze_router
from app.routers.auth import router as auth_router
from app.routers.billing import router as billing_router
from app.routers.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialise database tables
    from app.database import init_db
    init_db()

    # Kick off background model downloads so the first real request is fast.
    try:
        from app.services.ml_detector import preload_models
        preload_models()
    except Exception:
        pass  # non-fatal — heuristics still work without ML
    yield


app = FastAPI(
    lifespan=lifespan,
    title="VeritasAI",
    description="AI-Generated Content Detection & Media Authentication API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://localhost:80",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(analyze_router)
app.include_router(auth_router)
app.include_router(billing_router)
app.include_router(admin_router)


@app.get("/")
async def root():
    return {
        "service": "VeritasAI",
        "version": "1.0.0",
        "docs": "/api/docs",
        "endpoints": {
            "analyze": "POST /api/analyze",
            "report": "GET /api/report/{job_id}",
            "result": "GET /api/result/{job_id}",
            "health": "GET /api/health",
            "auth": {
                "register": "POST /api/auth/register",
                "login": "POST /api/auth/login",
                "me": "GET /api/auth/me",
                "forgot_password": "POST /api/auth/forgot-password",
                "reset_password": "POST /api/auth/reset-password",
            },
            "billing": {
                "plans": "GET /api/billing/plans",
                "checkout": "POST /api/billing/create-checkout",
                "portal": "POST /api/billing/portal",
                "webhook": "POST /api/billing/webhook",
            },
        },
    }
