"""
Main analysis router.
POST /api/analyze  — upload file and run full analysis pipeline
GET  /api/report/{job_id} — download PDF report
"""
import io
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response, StreamingResponse

from app.models.analysis import (
    AnalysisResult, C2PAResult, DetectionSignal, FileType, MetadataField,
    SignalSeverity,
)
from app.services.ai_detector import (
    analyze_document, analyze_image, analyze_presentation, analyze_spreadsheet,
)
from app.services.c2pa import check_c2pa
from app.services.metadata import extract_metadata
from app.services.report_gen import generate_pdf_report
from app.routers.auth import get_optional_user
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api", tags=["analysis"])

# In-memory report cache (job_id → bytes)
_report_cache: dict[str, bytes] = {}
_result_cache: dict[str, AnalysisResult] = {}

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

MIME_TO_FILE_TYPE = {
    # Images
    "image/jpeg": FileType.IMAGE,
    "image/png": FileType.IMAGE,
    "image/webp": FileType.IMAGE,
    "image/gif": FileType.IMAGE,
    "image/tiff": FileType.IMAGE,
    "image/bmp": FileType.IMAGE,
    "image/heic": FileType.IMAGE,
    "image/heif": FileType.IMAGE,
    # Documents
    "application/pdf": FileType.DOCUMENT,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": FileType.DOCUMENT,
    "application/msword": FileType.DOCUMENT,
    # Presentations
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": FileType.PRESENTATION,
    "application/vnd.ms-powerpoint": FileType.PRESENTATION,
    # Spreadsheets
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": FileType.SPREADSHEET,
    "application/vnd.ms-excel": FileType.SPREADSHEET,
    "text/csv": FileType.SPREADSHEET,
    "text/plain": FileType.SPREADSHEET,  # .csv files sometimes detected as text/plain
}

ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".tiff", ".bmp", ".heic", ".heif",
    ".pdf", ".docx", ".doc",
    ".pptx", ".ppt",
    ".xlsx", ".xls", ".csv",
}


def _detect_mime(file_path: Path, original_mime: str) -> str:
    """Best-effort MIME detection."""
    try:
        import magic
        return magic.from_file(str(file_path), mime=True)
    except Exception:
        pass
    ext = file_path.suffix.lower()
    ext_mime = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".webp": "image/webp", ".gif": "image/gif", ".tiff": "image/tiff",
        ".bmp": "image/bmp",
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".doc": "application/msword",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".ppt": "application/vnd.ms-powerpoint",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
        ".csv": "text/csv",
    }
    return ext_mime.get(ext, original_mime or "application/octet-stream")


def _compute_verdict(ai_prob: float, confidence: float):
    if ai_prob >= 0.80:
        return "AI-Generated", "red"
    elif ai_prob >= 0.60:
        return "Likely AI-Generated", "orange"
    elif ai_prob >= 0.40:
        return "Uncertain", "yellow"
    elif ai_prob >= 0.20:
        return "Likely Authentic", "green"
    else:
        return "Authentic", "green"


def _compute_confidence(signals: list, n_signals: int) -> float:
    """Confidence = how many signals agree with the overall direction."""
    if not signals:
        return 0.3
    high_count = sum(1 for s in signals if s.severity == SignalSeverity.HIGH)
    med_count = sum(1 for s in signals if s.severity == SignalSeverity.MEDIUM)
    base = (high_count * 0.4 + med_count * 0.2) / max(n_signals, 1)
    return min(0.3 + base * 2, 0.98)


def _check_rate_limit(user, db: Session):
    """Enforce daily scan limits. Resets at midnight UTC."""
    from app.routers.auth import PLAN_DAILY_LIMITS
    if user is None:
        return  # anonymous — allow (no per-IP limit in this implementation)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if user.last_scan_date != today:
        user.daily_scans = 0
        user.last_scan_date = today
    limit = PLAN_DAILY_LIMITS.get(user.plan, 10)
    if user.daily_scans >= limit:
        raise HTTPException(
            429,
            f"Daily scan limit reached ({limit}/day on {user.plan} plan). "
            "Upgrade at /pricing for more scans.",
        )
    user.daily_scans += 1
    db.commit()


@router.post("/analyze")
async def analyze_file(
    file: UploadFile = File(...),
    niche: Optional[str] = Form(None),
    current_user=Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    _check_rate_limit(current_user, db)
    start_ms = int(time.time() * 1000)
    job_id = str(uuid.uuid4())

    # ── Validate ──────────────────────────────────────────────────────
    if not file.filename:
        raise HTTPException(400, "No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    # Save to disk
    save_path = UPLOAD_DIR / f"{job_id}{ext}"
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large (max 100 MB)")

    async with aiofiles.open(save_path, "wb") as f:
        await f.write(content)

    # ── Detect MIME ───────────────────────────────────────────────────
    mime_type = _detect_mime(save_path, file.content_type or "")
    file_type = MIME_TO_FILE_TYPE.get(mime_type, FileType.UNKNOWN)

    # ── Run analysis pipeline ─────────────────────────────────────────
    try:
        # 1. Metadata extraction
        metadata = await extract_metadata(save_path, mime_type)

        # 2. C2PA check
        c2pa_result = await check_c2pa(save_path, mime_type)

        # 3. AI detection
        if file_type == FileType.IMAGE:
            ai_prob, signals = await analyze_image(save_path)
        elif file_type == FileType.DOCUMENT:
            ai_prob, signals = await analyze_document(save_path, mime_type)
        elif file_type == FileType.PRESENTATION:
            ai_prob, signals = await analyze_presentation(save_path, mime_type)
        elif file_type == FileType.SPREADSHEET:
            ai_prob, signals = await analyze_spreadsheet(save_path, mime_type)
        else:
            ai_prob = 0.3
            signals = [DetectionSignal(
                name="Unsupported File Type",
                description="Deep analysis not available for this file type.",
                severity=SignalSeverity.LOW,
                score=0.3,
            )]

        # 4. Boost score if metadata flags AI tools
        meta_suspicious = sum(1 for m in metadata if m.suspicious)
        if meta_suspicious >= 2:
            ai_prob = min(ai_prob + 0.15, 1.0)
        elif meta_suspicious == 1:
            ai_prob = min(ai_prob + 0.07, 1.0)

        # If no C2PA but suspicious, add a small penalty
        if not c2pa_result.has_credentials and ai_prob > 0.4:
            ai_prob = min(ai_prob + 0.03, 1.0)

        confidence = _compute_confidence(signals, len(signals))
        verdict, verdict_color = _compute_verdict(ai_prob, confidence)

        # Sub-scores
        def avg_score(indices):
            sigs = [signals[i] for i in indices if i < len(signals)]
            return sum(s.score for s in sigs) / len(sigs) if sigs else 0.0

        if file_type == FileType.IMAGE and len(signals) >= 4:
            meta_score = signals[0].score
            artifact_score = signals[1].score
            freq_score = signals[3].score
            consistency_score = signals[2].score
        else:
            meta_score = sum(1 for m in metadata if m.suspicious) / max(len(metadata), 1)
            artifact_score = ai_prob
            freq_score = ai_prob * 0.9
            consistency_score = confidence

        duration_ms = int(time.time() * 1000) - start_ms

        result = AnalysisResult(
            job_id=job_id,
            filename=file.filename,
            file_type=file_type,
            file_size_bytes=len(content),
            mime_type=mime_type,
            ai_probability=round(ai_prob, 4),
            confidence=round(confidence, 4),
            verdict=verdict,
            verdict_color=verdict_color,
            signals=signals,
            metadata=metadata,
            c2pa=c2pa_result,
            metadata_score=round(meta_score, 4),
            artifact_score=round(artifact_score, 4),
            frequency_score=round(freq_score, 4),
            consistency_score=round(consistency_score, 4),
            analysis_duration_ms=duration_ms,
            analyzed_at=datetime.now(timezone.utc).isoformat(),
        )

        # Generate and cache PDF report
        pdf_bytes = generate_pdf_report(result)
        _report_cache[job_id] = pdf_bytes
        _result_cache[job_id] = result

        return result

    finally:
        # Clean up uploaded file
        try:
            save_path.unlink(missing_ok=True)
        except Exception:
            pass


@router.get("/report/{job_id}")
async def download_report(job_id: str):
    if job_id not in _report_cache:
        raise HTTPException(404, "Report not found. Run analysis first.")

    pdf_bytes = _report_cache[job_id]
    result = _result_cache.get(job_id)
    filename = f"veritasai_report_{job_id[:8]}.pdf"
    if result:
        safe_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in result.filename)
        filename = f"veritasai_{safe_name}_{job_id[:8]}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/result/{job_id}")
async def get_result(job_id: str):
    if job_id not in _result_cache:
        raise HTTPException(404, "Result not found.")
    return _result_cache[job_id]


@router.get("/health")
async def health():
    return {"status": "ok", "service": "VeritasAI"}
