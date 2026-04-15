"""
AI-generated content detection service.

Detection layers (in order of reliability):
  1. ML Neural-Network classifier  — primary signal when available
  2. Forensic heuristics           — corroborating evidence

Weights when ML is available:
  Images    — ML 60 % + heuristics 40 %
  Documents — ML 55 % + heuristics 45 %
  Audio     — metadata 30 % + format 25 % + spectral 45 %

Weights when ML is NOT available (torch not installed):
  Images    — ELA 28 % + EXIF 18 % + Noise 22 % + Freq 16 % + Color 9 % + Texture 7 %
  Documents — Burstiness 28 % + Phrases 25 % + Vocab 22 % + Para-homogeneity 14 % + Self-similarity 11 %
"""

import io
import logging
import math
import re
from pathlib import Path
from typing import List, Optional, Tuple

from app.models.analysis import DetectionSignal, SignalSeverity

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# IMAGE ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

async def analyze_image(file_path: Path) -> Tuple[float, List[DetectionSignal]]:
    """Returns (ai_probability 0-1, signals)."""
    signals: List[DetectionSignal] = []

    try:
        from PIL import Image
        import numpy as np

        img = Image.open(file_path).convert("RGB")
        arr = np.array(img, dtype=np.float32)

        # ── 1. ML classifier (primary signal) ─────────────────────────────
        ml_prob, ml_weight = _ml_image_signal(file_path, signals)

        # ── 2-7. Forensic heuristics ───────────────────────────────────────
        exif_score,  exif_sig  = _check_exif_presence(file_path, img)
        ela_score,   ela_sig   = _ela_analysis(img)
        noise_score, noise_sig = _noise_analysis(arr)
        freq_score,  freq_sig  = _frequency_analysis(arr)
        color_score, color_sig = _color_distribution(arr)
        tex_score,   tex_sig   = _texture_regularity(arr)

        signals += [exif_sig, ela_sig, noise_sig, freq_sig, color_sig, tex_sig]
        h_scores = [exif_score, ela_score, noise_score, freq_score, color_score, tex_score]

        if ml_prob is not None:
            # ML available: 60 % ML + 40 % heuristics
            h_weights = [0.12, 0.10, 0.08, 0.06, 0.02, 0.02]  # sum = 0.40
            h_prob = sum(s * w for s, w in zip(h_scores, h_weights))
            ai_prob = ml_prob * ml_weight + h_prob
        else:
            # Heuristics only
            h_weights = [0.18, 0.28, 0.22, 0.16, 0.09, 0.07]  # sum = 1.00
            ai_prob = sum(s * w for s, w in zip(h_scores, h_weights))

    except Exception as exc:
        logger.exception("Image analysis failed")
        signals.append(DetectionSignal(
            name="Image Analysis Error",
            description=str(exc),
            severity=SignalSeverity.LOW,
            score=0.0,
        ))
        return 0.5, signals

    return float(min(max(ai_prob, 0.0), 1.0)), signals


def _ml_image_signal(
    file_path: Path,
    signals: List[DetectionSignal],
) -> Tuple[Optional[float], float]:
    """
    Attempt ML classification. Appends a signal and returns
    (ml_probability, ml_weight) or (None, 0) if unavailable.
    """
    try:
        from app.services.ml_detector import ml_image_score
        ml_prob, details = ml_image_score(file_path)
        if ml_prob is None:
            return None, 0.0

        if ml_prob >= 0.70:
            severity = SignalSeverity.HIGH
        elif ml_prob >= 0.40:
            severity = SignalSeverity.MEDIUM
        else:
            severity = SignalSeverity.LOW

        signals.append(DetectionSignal(
            name="Neural Network Classifier",
            description=(
                f"Vision Transformer trained on hundreds of thousands of AI-generated "
                f"and real images. Confidence: {ml_prob:.1%} AI-generated."
            ),
            severity=severity,
            score=ml_prob,
            details=details,
        ))
        return ml_prob, 0.60

    except Exception as exc:
        logger.warning("ML image signal failed: %s", exc)
        return None, 0.0


# ─────────────────────────────────────────────────────────────────────────────
# DOCUMENT ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

async def analyze_document(file_path: Path, mime_type: str) -> Tuple[float, List[DetectionSignal]]:
    """Returns (ai_probability, signals)."""
    signals: List[DetectionSignal] = []

    text = ""
    try:
        if mime_type == "application/pdf":
            text = _extract_pdf_text(file_path)
        else:
            text = _extract_docx_text(file_path)
    except Exception:
        pass

    if not text.strip():
        signals.append(DetectionSignal(
            name="Empty Document",
            description="No extractable text found.",
            severity=SignalSeverity.LOW,
            score=0.0,
        ))
        return 0.3, signals

    # ── 1. RoBERTa ML classifier ───────────────────────────────────────────
    ml_prob, _ml_weight = _ml_text_signal(text, signals)

    # ── 2. GPT-2 perplexity (works on short/structured text too) ──────────
    perp_score, perp_sig = _perplexity_signal(text, signals)

    # ── 3. Template / placeholder detector ────────────────────────────────
    tmpl_score, tmpl_sig = _template_placeholder_check(text)

    # ── 4. Professional AI buzzwords ──────────────────────────────────────
    buzz_score, buzz_sig = _professional_buzzwords(text)

    # ── 5-9. Linguistic heuristics ─────────────────────────────────────────
    burst_score,  burst_sig  = _text_burstiness(text)
    vocab_score,  vocab_sig  = _vocabulary_richness(text)
    phrase_score, phrase_sig = _transition_phrases(text)
    para_score,   para_sig   = _paragraph_homogeneity(text)
    sim_score,    sim_sig    = _sentence_self_similarity(text)

    signals += [perp_sig, tmpl_sig, buzz_sig, burst_sig, vocab_sig, phrase_sig, para_sig, sim_sig]
    h_scores = [tmpl_score, buzz_score, burst_score, vocab_score, phrase_score, para_score, sim_score]

    # Perplexity: cap minimum at 0.38 so it can't actively drag scores down
    # (high-jargon/structured text inflates GPT-2 perplexity unfairly)
    p = max(perp_score, 0.38) if perp_score is not None else 0.45

    if ml_prob is not None:
        # RoBERTa 15% + GPT-2 perplexity 20% + heuristics 65%
        # RoBERTa is down-weighted — it fails on bullet-point / short structured text
        # Template + buzzwords get highest heuristic weight (most reliable signals)
        h_weights = [0.18, 0.14, 0.09, 0.07, 0.09, 0.04, 0.04]  # sum = 0.65
        h_prob = sum(s * w for s, w in zip(h_scores, h_weights))
        ai_prob = ml_prob * 0.15 + p * 0.20 + h_prob
    else:
        # No ML: heuristics carry full weight
        h_weights = [0.25, 0.22, 0.14, 0.12, 0.15, 0.07, 0.05]  # sum = 1.00
        ai_prob = sum(s * w for s, w in zip(h_scores, h_weights))

    # High-confidence individual signals set a minimum floor:
    # Template placeholders or dense buzzwords are near-definitive — don't let
    # weak signals from other checks drag the score below what they imply.
    if tmpl_score >= 0.80:
        ai_prob = max(ai_prob, 0.72)
    elif buzz_score >= 0.80 and phrase_score >= 0.60:
        ai_prob = max(ai_prob, 0.62)

    return float(min(max(ai_prob, 0.0), 1.0)), signals


def _ml_text_signal(
    text: str,
    signals: List[DetectionSignal],
) -> Tuple[Optional[float], float]:
    try:
        from app.services.ml_detector import ml_text_score
        ml_prob, details = ml_text_score(text)
        if ml_prob is None:
            return None, 0.0

        if ml_prob >= 0.70:
            severity = SignalSeverity.HIGH
        elif ml_prob >= 0.40:
            severity = SignalSeverity.MEDIUM
        else:
            severity = SignalSeverity.LOW

        signals.append(DetectionSignal(
            name="Neural Network Text Classifier",
            description=(
                f"RoBERTa model fine-tuned to distinguish human vs AI-generated text. "
                f"Confidence: {ml_prob:.1%} AI-generated."
            ),
            severity=severity,
            score=ml_prob,
            details=details,
        ))
        return ml_prob, 0.55

    except Exception as exc:
        logger.warning("ML text signal failed: %s", exc)
        return None, 0.0


# ─────────────────────────────────────────────────────────────────────────────
# AUDIO ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

async def analyze_audio(file_path: Path) -> Tuple[float, List[DetectionSignal]]:
    """Returns (ai_probability, signals)."""
    signals: List[DetectionSignal] = []

    meta_score,    meta_sig    = _audio_metadata_check(file_path)
    fmt_score,     fmt_sig     = _audio_format_check(file_path)
    spectral_score, spectral_sig = _audio_spectral_analysis(file_path)

    signals += [meta_sig, fmt_sig, spectral_sig]

    # spectral analysis gets the most weight — most diagnostic
    ai_prob = meta_score * 0.30 + fmt_score * 0.25 + spectral_score * 0.45
    return float(min(max(ai_prob, 0.0), 1.0)), signals


# ─────────────────────────────────────────────────────────────────────────────
# VIDEO ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

async def analyze_video(file_path: Path) -> Tuple[float, List[DetectionSignal]]:
    """Returns (ai_probability, signals)."""
    signals: List[DetectionSignal] = []

    try:
        frame_score, frame_signals = await _extract_and_analyze_frame(file_path)
        signals.extend(frame_signals)
        container_score, container_signal = _video_container_check(file_path)
        signals.append(container_signal)
        ai_prob = frame_score * 0.7 + container_score * 0.3
        return float(min(max(ai_prob, 0.0), 1.0)), signals
    except Exception as exc:
        signals.append(DetectionSignal(
            name="Video Analysis",
            description=f"Frame extraction unavailable: {exc}",
            severity=SignalSeverity.LOW,
            score=0.3,
        ))
        return 0.3, signals


# ─────────────────────────────────────────────────────────────────────────────
# IMAGE FORENSIC HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _check_exif_presence(file_path: Path, img) -> Tuple[float, DetectionSignal]:
    """
    AI generators almost never embed authentic camera EXIF.

    Calibration note:
      - "No EXIF" is a *weak* signal (screenshots, social-media images, web downloads
        all lack EXIF legitimately). Cap at 0.60 to reduce false positives.
      - "Full camera EXIF" is a strong negative signal (very hard to fake convincingly).
    """
    try:
        import exifread
        with open(file_path, "rb") as f:
            tags = exifread.process_file(f, details=False)

        has_camera = any("Make" in k or "Model" in k for k in tags)
        has_gps    = any("GPS" in k for k in tags)
        has_lens   = any("Lens" in k for k in tags)
        has_datetime = any("DateTime" in k for k in tags)

        if not tags:
            return 0.60, DetectionSignal(
                name="No EXIF Metadata",
                description=(
                    "File has no EXIF data. Authentic camera photos always contain "
                    "hardware metadata; AI generators do not embed EXIF."
                ),
                severity=SignalSeverity.MEDIUM,
                score=0.60,
                details="Note: screenshots and socially-shared images also lack EXIF.",
            )

        if not has_camera:
            return 0.50, DetectionSignal(
                name="Missing Camera Hardware Info",
                description="EXIF present but lacks camera make/model — unusual for real photos.",
                severity=SignalSeverity.MEDIUM,
                score=0.50,
            )

        detail = f"Camera: {tags.get('Image Make', '?')} {tags.get('Image Model', '?')}"
        if has_gps:
            detail += " | GPS data present"
        if has_lens:
            detail += " | Lens info present"
        if has_datetime:
            detail += f" | Taken: {tags.get('Image DateTime', '?')}"

        return 0.08, DetectionSignal(
            name="Camera EXIF Present",
            description="Full camera hardware metadata found. Consistent with authentic photography.",
            severity=SignalSeverity.LOW,
            score=0.08,
            details=detail,
        )
    except Exception:
        return 0.45, DetectionSignal(
            name="EXIF Check Failed",
            description="Could not parse EXIF data.",
            severity=SignalSeverity.LOW,
            score=0.45,
        )


def _ela_analysis(img) -> Tuple[float, DetectionSignal]:
    """
    Error Level Analysis — resave at known JPEG quality and measure pixel delta.
    AI-generated images have characteristically uniform ELA across the whole image.

    Fixed vs previous version:
      - PNG/non-JPEG inputs: the first JPEG save introduces pervasive compression
        artifacts, so we use a higher quality (92) to reduce that artefact and
        recalibrate thresholds accordingly.
    """
    try:
        import numpy as np
        from PIL import Image

        img_rgb = img.convert("RGB")
        is_jpeg = getattr(img, "format", "") in ("JPEG", "JPG")
        quality = 75 if is_jpeg else 92  # higher quality for non-JPEG to reduce noise

        buf = io.BytesIO()
        img_rgb.save(buf, format="JPEG", quality=quality)
        buf.seek(0)
        img_resaved = Image.open(buf).convert("RGB")

        orig = np.array(img_rgb,  dtype=np.float32)
        resd = np.array(img_resaved, dtype=np.float32)
        ela  = np.abs(orig - resd)

        mean_ela = float(ela.mean())
        std_ela  = float(ela.std())

        h, w = ela.shape[:2]
        block = 32
        block_means = [
            ela[y:y + block, x:x + block].mean()
            for y in range(0, h - block, block)
            for x in range(0, w - block, block)
        ]
        block_cv = float(
            np.array(block_means).std() / (np.array(block_means).mean() + 1e-6)
        )

        # Recalibrated thresholds (less aggressive than v1)
        if block_cv < 0.35 and mean_ela < 10.0:
            score, severity = 0.72, SignalSeverity.HIGH
            desc = (
                f"Suspiciously uniform ELA (mean={mean_ela:.1f}, CV={block_cv:.2f}). "
                "AI images lack natural JPEG re-compression variance."
            )
        elif block_cv < 0.60 or mean_ela < 6.0:
            score, severity = 0.42, SignalSeverity.MEDIUM
            desc = (
                f"Moderately uniform ELA (mean={mean_ela:.1f}, CV={block_cv:.2f}). "
                "Some regions show inconsistent compression history."
            )
        else:
            score, severity = 0.12, SignalSeverity.LOW
            desc = (
                f"Natural ELA variation (mean={mean_ela:.1f}, CV={block_cv:.2f}). "
                "Consistent with real-world photography."
            )

        return score, DetectionSignal(
            name="Error Level Analysis (ELA)",
            description=desc,
            severity=severity,
            score=score,
            details=f"Mean={mean_ela:.2f} | Std={std_ela:.2f} | Block CV={block_cv:.3f} | Input={'JPEG' if is_jpeg else 'non-JPEG'}",
        )
    except Exception as exc:
        return 0.45, DetectionSignal(
            name="ELA Analysis Failed",
            description=str(exc),
            severity=SignalSeverity.LOW,
            score=0.45,
        )


def _noise_analysis(arr) -> Tuple[float, DetectionSignal]:
    """
    Camera sensors produce unique, near-white noise patterns.
    AI generators produce images with unnaturally smooth or correlated noise.
    """
    try:
        import numpy as np
        from scipy.ndimage import gaussian_filter

        gray   = arr.mean(axis=2)
        smooth = gaussian_filter(gray, sigma=2)
        noise  = gray - smooth

        noise_std = float(noise.std())

        h, w   = noise.shape
        sample = noise[:min(h, 256), :min(w, 256)].flatten()
        if len(sample) > 1:
            with np.errstate(invalid="ignore"):
                corr = np.corrcoef(sample[:-1], sample[1:])
            ac = float(corr[0, 1]) if not np.isnan(corr[0, 1]) else 0.0
        else:
            ac = 0.0

        if noise_std < 2.5:
            score, severity = 0.78, SignalSeverity.HIGH
            desc = f"Extremely low noise (σ={noise_std:.2f}). AI generators produce unrealistically clean images."
        elif noise_std < 5.0 and abs(ac) > 0.15:
            score, severity = 0.58, SignalSeverity.MEDIUM
            desc = f"Correlated noise (σ={noise_std:.2f}, AC={ac:.3f}). May indicate synthetic generation or heavy post-processing."
        elif abs(ac) > 0.25:
            score, severity = 0.48, SignalSeverity.MEDIUM
            desc = f"Spatially correlated noise (AC={ac:.3f}). Natural sensor noise is typically uncorrelated."
        else:
            score, severity = 0.12, SignalSeverity.LOW
            desc = f"Natural noise pattern (σ={noise_std:.2f}, AC={ac:.3f}). Consistent with real sensor noise."

        return score, DetectionSignal(
            name="Noise Pattern Analysis",
            description=desc,
            severity=severity,
            score=score,
            details=f"Noise σ={noise_std:.3f} | AC={ac:.4f}",
        )
    except Exception as exc:
        return 0.45, DetectionSignal(
            name="Noise Analysis Failed",
            description=str(exc),
            severity=SignalSeverity.LOW,
            score=0.45,
        )


def _frequency_analysis(arr) -> Tuple[float, DetectionSignal]:
    """
    DCT/FFT frequency domain analysis.
    Diffusion models produce images with anomalous high-frequency energy distribution.
    """
    try:
        import numpy as np

        gray = arr.mean(axis=2)
        h, w = gray.shape
        cy, cx = h // 2, w // 2
        size   = min(256, cy, cx)
        crop   = gray[cy - size:cy + size, cx - size:cx + size]

        fft_shift = np.fft.fftshift(np.fft.fft2(crop))
        magnitude = np.log1p(np.abs(fft_shift))

        mid_y, mid_x = magnitude.shape[0] // 2, magnitude.shape[1] // 2
        Y, X  = np.ogrid[:magnitude.shape[0], :magnitude.shape[1]]
        dist  = np.sqrt((Y - mid_y) ** 2 + (X - mid_x) ** 2)
        max_r = min(mid_y, mid_x)

        low_e  = float(magnitude[dist < max_r * 0.2].mean())
        mid_e  = float(magnitude[(dist >= max_r * 0.2) & (dist < max_r * 0.5)].mean())
        high_e = float(magnitude[dist >= max_r * 0.5].mean())

        ratio_hl = high_e / (low_e + 1e-6)

        if ratio_hl > 0.88:
            score, severity = 0.68, SignalSeverity.HIGH
            desc = f"Anomalous high-frequency energy (H/L={ratio_hl:.2f}). Diffusion models produce distinctive spectral signatures."
        elif ratio_hl > 0.72:
            score, severity = 0.42, SignalSeverity.MEDIUM
            desc = f"Elevated high-frequency energy (H/L={ratio_hl:.2f}). May indicate AI generation or heavy sharpening."
        else:
            score, severity = 0.12, SignalSeverity.LOW
            desc = f"Normal frequency distribution (H/L={ratio_hl:.2f}). Consistent with natural imagery."

        return score, DetectionSignal(
            name="DCT Frequency Analysis",
            description=desc,
            severity=severity,
            score=score,
            details=f"Low={low_e:.3f} | Mid={mid_e:.3f} | High={high_e:.3f} | H/L={ratio_hl:.3f}",
        )
    except Exception as exc:
        return 0.45, DetectionSignal(
            name="Frequency Analysis Failed",
            description=str(exc),
            severity=SignalSeverity.LOW,
            score=0.45,
        )


def _color_distribution(arr) -> Tuple[float, DetectionSignal]:
    """AI-generated images often exhibit over-saturated or hyper-consistent colour distributions."""
    try:
        import numpy as np

        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        r_std, g_std, b_std = float(r.std()), float(g.std()), float(b.std())

        rg_corr = float(np.corrcoef(r.flatten()[:10000], g.flatten()[:10000])[0, 1])
        mean_sat = float(_compute_saturation(arr).mean())

        if mean_sat > 0.78 and rg_corr > 0.95:
            score, severity = 0.62, SignalSeverity.MEDIUM
            desc = f"High saturation (S={mean_sat:.2f}) + channel correlation ({rg_corr:.2f}). AI images often over-saturate."
        elif r_std < 20 and g_std < 20 and b_std < 20:
            score, severity = 0.52, SignalSeverity.MEDIUM
            desc = f"Very low colour variance (R={r_std:.1f}, G={g_std:.1f}, B={b_std:.1f}). Unnaturally homogeneous."
        else:
            score, severity = 0.18, SignalSeverity.LOW
            desc = f"Normal colour distribution (saturation={mean_sat:.2f}). No anomalies detected."

        return score, DetectionSignal(
            name="Colour Distribution Analysis",
            description=desc,
            severity=severity,
            score=score,
            details=f"R σ={r_std:.1f} | G σ={g_std:.1f} | B σ={b_std:.1f} | Sat={mean_sat:.3f}",
        )
    except Exception as exc:
        return 0.45, DetectionSignal(
            name="Colour Analysis Failed",
            description=str(exc),
            severity=SignalSeverity.LOW,
            score=0.45,
        )


def _compute_saturation(arr):
    import numpy as np
    a = arr / 255.0
    c_max, c_min = a.max(axis=2), a.min(axis=2)
    return np.where(c_max > 0, (c_max - c_min) / (c_max + 1e-6), 0)


def _texture_regularity(arr) -> Tuple[float, DetectionSignal]:
    """AI images often have suspiciously uniform textures across the frame."""
    try:
        import numpy as np
        from scipy.ndimage import sobel

        gray = arr.mean(axis=2)
        h, w = gray.shape

        edges = np.sqrt(sobel(gray, axis=0) ** 2 + sobel(gray, axis=1) ** 2)
        block = 32
        densities = [
            float(edges[y:y + block, x:x + block].mean())
            for y in range(0, h - block, block)
            for x in range(0, w - block, block)
        ]
        d = np.array(densities)
        cv = float(d.std() / (d.mean() + 1e-6))

        if cv < 0.28:
            score, severity = 0.68, SignalSeverity.HIGH
            desc = f"Suspiciously regular texture (CV={cv:.3f}). AI images lack natural texture variation."
        elif cv < 0.52:
            score, severity = 0.38, SignalSeverity.MEDIUM
            desc = f"Moderately uniform texture (CV={cv:.3f})."
        else:
            score, severity = 0.12, SignalSeverity.LOW
            desc = f"Natural texture variation (CV={cv:.3f})."

        return score, DetectionSignal(
            name="Texture Regularity",
            description=desc,
            severity=severity,
            score=score,
            details=f"Edge density mean={d.mean():.2f} | std={d.std():.2f} | CV={cv:.4f}",
        )
    except Exception as exc:
        return 0.45, DetectionSignal(
            name="Texture Analysis Failed",
            description=str(exc),
            severity=SignalSeverity.LOW,
            score=0.45,
        )


# ─────────────────────────────────────────────────────────────────────────────
# DOCUMENT TEXT HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _extract_pdf_text(file_path: Path) -> str:
    import PyPDF2
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        return "\n".join(page.extract_text() or "" for page in reader.pages[:20])


def _extract_docx_text(file_path: Path) -> str:
    from docx import Document
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)


def _split_into_units(text: str):
    """
    Split text into analysable units including bullet points and numbered lists,
    not just prose sentences ending in .!?
    """
    # Split on sentence endings AND newlines (for bullet-point structured docs)
    raw = re.split(r"[.!?]+|\n+", text)
    return [s.strip() for s in raw if 2 <= len(s.split()) <= 80]


def _text_burstiness(text: str) -> Tuple[float, DetectionSignal]:
    """
    Burstiness = variability in sentence / unit length.
    Human writing is "bursty"; AI text is uniformly structured.
    Also works on bullet-point CVs and structured documents.
    """
    units = _split_into_units(text)
    lengths = [len(s.split()) for s in units]

    if len(lengths) < 4:
        return 0.3, DetectionSignal(
            name="Sentence Burstiness",
            description="Too few units to analyse.",
            severity=SignalSeverity.LOW,
            score=0.3,
        )

    mean_l = sum(lengths) / len(lengths)
    std_l  = math.sqrt(sum((x - mean_l) ** 2 for x in lengths) / len(lengths))
    cv     = std_l / (mean_l + 1e-6)

    if cv < 0.25:
        score, severity = 0.75, SignalSeverity.HIGH
        desc = f"Low burstiness (CV={cv:.2f}). AI text has more uniform sentence lengths than human writing."
    elif cv < 0.40:
        score, severity = 0.48, SignalSeverity.MEDIUM
        desc = f"Moderate burstiness (CV={cv:.2f}). Somewhat uniform sentence structure."
    else:
        score, severity = 0.12, SignalSeverity.LOW
        desc = f"Natural burstiness (CV={cv:.2f}). Length variety consistent with human authorship."

    return score, DetectionSignal(
        name="Sentence Length Burstiness",
        description=desc,
        severity=severity,
        score=score,
        details=f"Mean={mean_l:.1f} words | Std={std_l:.1f} | CV={cv:.3f}",
    )


def _vocabulary_richness(text: str) -> Tuple[float, DetectionSignal]:
    """Type-Token Ratio — AI text reuses vocabulary more than humans."""
    words = re.findall(r"\b[a-z]+\b", text.lower())
    if len(words) < 50:
        return 0.3, DetectionSignal(
            name="Vocabulary Richness",
            description="Insufficient text for vocabulary analysis.",
            severity=SignalSeverity.LOW,
            score=0.3,
        )

    window = 100
    ttrs = [
        len(set(words[i:i + window])) / window
        for i in range(0, len(words) - window, window)
    ]
    mean_ttr = sum(ttrs) / len(ttrs) if ttrs else 0.5

    if mean_ttr > 0.75:
        score, severity = 0.12, SignalSeverity.LOW
        desc = f"High vocabulary richness (TTR={mean_ttr:.2f}). Diverse word choice → human authorship."
    elif mean_ttr > 0.60:
        score, severity = 0.32, SignalSeverity.LOW
        desc = f"Average vocabulary richness (TTR={mean_ttr:.2f})."
    else:
        score, severity = 0.65, SignalSeverity.MEDIUM
        desc = f"Low vocabulary richness (TTR={mean_ttr:.2f}). Repetitive word choice is a marker of AI text."

    return score, DetectionSignal(
        name="Vocabulary Richness (TTR)",
        description=desc,
        severity=severity,
        score=score,
        details=f"TTR={mean_ttr:.3f} over {len(ttrs)} windows",
    )


def _transition_phrases(text: str) -> Tuple[float, DetectionSignal]:
    """AI text over-uses specific transitional phrases and filler constructs."""
    AI_TRANSITIONS = [
        # ── Classic AI essay phrases ──
        "in conclusion", "furthermore", "moreover", "it is important to note",
        "it is worth noting", "in summary", "to summarize", "as a result",
        "on the other hand", "in addition", "it should be noted",
        "in this context", "needless to say", "it goes without saying",
        "first and foremost", "last but not least", "to begin with",
        "in light of", "this allows", "this enables", "this ensures",
        "thus ensuring", "plays a crucial role", "it is crucial",
        "it is essential", "plays a vital role", "key role", "delve into",
        "dive into", "at the end of the day", "moving forward",
        "having said that", "with that being said", "it's worth mentioning",
        "as previously mentioned", "as mentioned earlier",
        # ── CV / professional AI buzzwords ──
        "results-driven", "results driven", "detail-oriented", "detail oriented",
        "quick learner", "fast learner", "proven track record",
        "strong ability to", "growing interest in", "passionate about",
        "highly motivated", "self-motivated", "self motivated",
        "team player", "go-getter", "fast-paced environment",
        "seeking to leverage", "seeking to utilize", "adept at",
        "proficient in", "well-versed in", "versed in",
        "dedicated to", "committed to", "striving to",
        "ensuring confidentiality", "attention to detail",
        "strong communication skills", "excellent communication",
        "analytical thinking", "analytical skills",
        "problem-solving skills", "problem solving skills",
        "data-driven", "data driven", "cross-functional",
        "stakeholder", "synergize", "leverage", "value-added",
        "actionable insights", "thought leader", "best practices",
        "continuous improvement", "proactive approach",
        "comprehensive understanding", "demonstrated ability",
        "with experience in", "experience in",
        "dynamic professional", "dynamic individual",
        "innovative solutions", "strategic thinking",
        "driving results", "impactful", "collaborative",
        # ── Structural AI giveaways ──
        "comprehensive", "multifaceted", "robust", "streamline",
        "cutting-edge", "state-of-the-art", "holistic approach",
        "tailor", "tailored", "bespoke", "seamlessly",
        "transformative", "empower", "foster", "facilitate",
        "spearhead", "spearheaded", "championed",
    ]
    lower      = text.lower()
    word_count = max(len(text.split()), 1)
    found      = [(p, lower.count(p)) for p in AI_TRANSITIONS if p in lower]
    total_hits = sum(c for _, c in found)
    density    = total_hits / (word_count / 100)

    if density > 3.0:
        score, severity = 0.80, SignalSeverity.HIGH
        top  = sorted(found, key=lambda x: x[1], reverse=True)[:5]
        desc = f"High AI phrase density ({density:.1f}/100 words). Top phrases: {', '.join(p for p, _ in top)}"
    elif density > 1.0:
        score, severity = 0.48, SignalSeverity.MEDIUM
        desc = f"Moderate AI phrase density ({density:.1f}/100 words)."
    else:
        score, severity = 0.08, SignalSeverity.LOW
        desc = f"Low AI phrase density ({density:.1f}/100 words)."

    return score, DetectionSignal(
        name="AI Transition Phrase Density",
        description=desc,
        severity=severity,
        score=score,
        details=f"Density={density:.2f}/100 words | Unique phrases: {len(found)}",
    )


def _paragraph_homogeneity(text: str) -> Tuple[float, DetectionSignal]:
    """AI tends to write paragraphs of very similar length."""
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip().split()) > 10]
    if len(paragraphs) < 3:
        return 0.3, DetectionSignal(
            name="Paragraph Homogeneity",
            description="Too few paragraphs to assess.",
            severity=SignalSeverity.LOW,
            score=0.3,
        )

    lengths = [len(p.split()) for p in paragraphs]
    mean_l  = sum(lengths) / len(lengths)
    std_l   = math.sqrt(sum((x - mean_l) ** 2 for x in lengths) / len(lengths))
    cv      = std_l / (mean_l + 1e-6)

    if cv < 0.20:
        score, severity = 0.70, SignalSeverity.HIGH
        desc = f"Highly uniform paragraph lengths (CV={cv:.2f}). AI produces paragraphs of near-identical length."
    elif cv < 0.40:
        score, severity = 0.38, SignalSeverity.MEDIUM
        desc = f"Somewhat uniform paragraphs (CV={cv:.2f})."
    else:
        score, severity = 0.12, SignalSeverity.LOW
        desc = f"Natural paragraph length variation (CV={cv:.2f})."

    return score, DetectionSignal(
        name="Paragraph Length Homogeneity",
        description=desc,
        severity=severity,
        score=score,
        details=f"Mean={mean_l:.0f} words | Std={std_l:.1f} | CV={cv:.3f}",
    )


def _sentence_self_similarity(text: str) -> Tuple[float, DetectionSignal]:
    """
    Measures lexical overlap between consecutive sentences using Jaccard similarity.
    AI text tends to stay on the same narrow vocabulary; human text shifts more.
    """
    sentences = [s for s in _split_into_units(text) if len(s.split()) > 3]
    if len(sentences) < 5:
        return 0.3, DetectionSignal(
            name="Sentence Self-Similarity",
            description="Too few sentences for self-similarity analysis.",
            severity=SignalSeverity.LOW,
            score=0.3,
        )

    vectors = [set(s.lower().split()) for s in sentences]
    sims = []
    for i in range(len(vectors)):
        for j in range(i + 1, min(i + 4, len(vectors))):
            a, b = vectors[i], vectors[j]
            union = a | b
            if union:
                sims.append(len(a & b) / len(union))

    mean_sim = sum(sims) / len(sims) if sims else 0.0

    if mean_sim > 0.22:
        score, severity = 0.65, SignalSeverity.MEDIUM
        desc = f"High sentence self-similarity ({mean_sim:.2f}). AI text reuses the same vocabulary within paragraphs."
    elif mean_sim > 0.12:
        score, severity = 0.35, SignalSeverity.LOW
        desc = f"Moderate sentence self-similarity ({mean_sim:.2f})."
    else:
        score, severity = 0.10, SignalSeverity.LOW
        desc = f"Low sentence self-similarity ({mean_sim:.2f}). Vocabulary shifts naturally — consistent with human writing."

    return score, DetectionSignal(
        name="Sentence Self-Similarity",
        description=desc,
        severity=severity,
        score=score,
        details=f"Mean Jaccard similarity={mean_sim:.3f} over {len(sims)} pairs",
    )


def _perplexity_signal(
    text: str,
    signals: List[DetectionSignal],
) -> Tuple[Optional[float], DetectionSignal]:
    """GPT-2 perplexity — lower = more predictable = more AI-like."""
    try:
        from app.services.ml_detector import ml_perplexity_score
        prob, details = ml_perplexity_score(text)
        if prob is None:
            sig = DetectionSignal(
                name="GPT-2 Perplexity",
                description="Perplexity analysis unavailable.",
                severity=SignalSeverity.LOW,
                score=0.45,
                details=details,
            )
            return None, sig

        if prob >= 0.75:
            severity = SignalSeverity.HIGH
        elif prob >= 0.50:
            severity = SignalSeverity.MEDIUM
        else:
            severity = SignalSeverity.LOW

        sig = DetectionSignal(
            name="GPT-2 Perplexity",
            description=(
                f"AI-generated text is statistically more predictable under language models. "
                f"This text scores {prob:.0%} AI-likelihood based on predictability."
            ),
            severity=severity,
            score=prob,
            details=details,
        )
        return prob, sig
    except Exception as exc:
        logger.warning("Perplexity signal failed: %s", exc)
        return None, DetectionSignal(
            name="GPT-2 Perplexity",
            description="Perplexity analysis failed.",
            severity=SignalSeverity.LOW,
            score=0.45,
        )


def _template_placeholder_check(text: str) -> Tuple[float, DetectionSignal]:
    """
    Detect template placeholders and generic fill-in-the-blank patterns.
    Brackets like [Your Name], 'Company Name', 'University Name' are
    strong indicators of AI-generated or template content.
    """
    PLACEHOLDER_PATTERNS = [
        r"\[your [^\]]{1,40}\]",        # [Your Full Name], [Your Email] …
        r"\[name\]", r"\[email\]",
        r"\[company[^\]]{0,20}\]",
        r"\[job title\]", r"\[position\]",
        r"\[university[^\]]{0,20}\]",
        r"\[degree[^\]]{0,20}\]",
        r"\[year[^\]]{0,10}\]",
        r"\byour full name\b",
        r"\bcompany name\b",
        r"\buniversity name\b",
        r"\bjob title\b\s*[-–]",
        r"\bdegree\b\s*[-–]\s*university",
        r"\bcity,\s*country\b",
        r"\(year\s*[-–]\s*present\)",
        r"\(year\)",
        r"\byour name\b",
        r"\byour email\b",
        r"\byour phone\b",
    ]
    lower = text.lower()
    found = []
    for pat in PLACEHOLDER_PATTERNS:
        matches = re.findall(pat, lower)
        found.extend(matches)

    count = len(found)
    if count >= 3:
        score, severity = 0.96, SignalSeverity.HIGH
        desc = (
            f"Found {count} template placeholders (e.g. {', '.join(repr(f) for f in found[:3])}). "
            "These are strong markers of AI-generated or template content."
        )
    elif count >= 1:
        score, severity = 0.82, SignalSeverity.HIGH
        desc = f"Found template placeholder: {', '.join(repr(f) for f in found)}. Indicates AI-generated or template content."
    else:
        score, severity = 0.05, SignalSeverity.LOW
        desc = "No template placeholders detected."

    return score, DetectionSignal(
        name="Template Placeholders",
        description=desc,
        severity=severity,
        score=score,
        details=f"Placeholders found: {count}",
    )


def _professional_buzzwords(text: str) -> Tuple[float, DetectionSignal]:
    """
    Detect high-density professional buzzwords that AI models overuse
    in CVs, cover letters, and business documents.
    """
    BUZZWORDS = [
        "results-driven", "results driven", "detail-oriented", "detail oriented",
        "quick learner", "fast learner", "proven track record",
        "strong ability", "growing interest", "passionate about",
        "highly motivated", "self-motivated", "team player",
        "fast-paced", "seeking to leverage", "adept at",
        "dedicated professional", "committed to excellence",
        "ensuring confidentiality", "data accuracy",
        "strong communication", "excellent communication",
        "analytical thinking", "problem-solving",
        "cross-functional", "stakeholder", "synergize",
        "actionable insights", "best practices",
        "continuous improvement", "proactive",
        "comprehensive understanding", "demonstrated ability",
        "dynamic professional", "innovative solutions",
        "strategic thinking", "driving results",
        "streamline", "cutting-edge", "holistic approach",
        "transformative", "empower", "spearhead",
        "leveraging", "value-added", "collaborative environment",
        "attention to detail", "time management",
        "communication skills", "teamwork",
    ]
    lower = text.lower()
    word_count = max(len(text.split()), 1)
    found = [(bw, lower.count(bw)) for bw in BUZZWORDS if bw in lower]
    total_hits = sum(c for _, c in found)
    density = total_hits / (word_count / 100)

    if density > 4.0 or len(found) >= 6:
        score, severity = 0.88, SignalSeverity.HIGH
        top = sorted(found, key=lambda x: x[1], reverse=True)[:5]
        desc = (
            f"Very high professional buzzword density ({density:.1f}/100 words, {len(found)} unique). "
            f"Top: {', '.join(bw for bw, _ in top)}. "
            "AI models saturate professional documents with these phrases."
        )
    elif density > 2.0 or len(found) >= 3:
        score, severity = 0.65, SignalSeverity.MEDIUM
        desc = f"Elevated buzzword density ({density:.1f}/100 words, {len(found)} unique). Common in AI-written professional content."
    elif len(found) >= 1:
        score, severity = 0.35, SignalSeverity.LOW
        desc = f"Low buzzword density ({density:.1f}/100 words). A few common professional phrases detected."
    else:
        score, severity = 0.08, SignalSeverity.LOW
        desc = "No notable professional AI buzzwords detected."

    return score, DetectionSignal(
        name="Professional AI Buzzwords",
        description=desc,
        severity=severity,
        score=score,
        details=f"Density={density:.2f}/100 words | Unique buzzwords: {len(found)}",
    )


# ─────────────────────────────────────────────────────────────────────────────
# AUDIO HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _audio_metadata_check(file_path: Path) -> Tuple[float, DetectionSignal]:
    try:
        from mutagen import File as MutagenFile
        audio = MutagenFile(file_path)
        if audio is None:
            return 0.50, DetectionSignal(
                name="Audio Metadata",
                description="Could not parse audio file.",
                severity=SignalSeverity.LOW,
                score=0.50,
            )

        if not audio.tags:
            return 0.55, DetectionSignal(
                name="Audio Metadata Absent",
                description="No ID3 / metadata tags found. Synthetic audio files often lack tagging.",
                severity=SignalSeverity.MEDIUM,
                score=0.55,
            )

        for k in ["TSSE", "TENC", "encoder", "encoded_by"]:
            if k in audio:
                enc = str(audio[k])
                from app.services.metadata import _flag_software
                susp, note = _flag_software(enc)
                if susp:
                    return 0.88, DetectionSignal(
                        name="AI Audio Tool Detected",
                        description=f"Encoder field references known AI tool: '{enc}'",
                        severity=SignalSeverity.HIGH,
                        score=0.88,
                        details=note,
                    )

        return 0.18, DetectionSignal(
            name="Audio Metadata Present",
            description="Standard audio metadata found. No AI tool markers detected.",
            severity=SignalSeverity.LOW,
            score=0.18,
        )
    except Exception as exc:
        return 0.40, DetectionSignal(
            name="Audio Metadata Error",
            description=str(exc),
            severity=SignalSeverity.LOW,
            score=0.40,
        )


def _audio_format_check(file_path: Path) -> Tuple[float, DetectionSignal]:
    """Sample rate and bitrate heuristics for TTS detection."""
    try:
        from mutagen import File as MutagenFile
        audio = MutagenFile(file_path)
        if audio is None or not hasattr(audio, "info"):
            return 0.40, DetectionSignal(
                name="Audio Format",
                description="Cannot determine audio format.",
                severity=SignalSeverity.LOW,
                score=0.40,
            )
        info     = audio.info
        duration = getattr(info, "length", 0)
        bitrate  = getattr(info, "bitrate", 0)
        sr       = getattr(info, "sample_rate", 0)

        suspicious_sr = sr in (16000, 22050, 24000)  # common TTS output rates

        if suspicious_sr and duration < 30:
            score, severity = 0.65, SignalSeverity.MEDIUM
            desc = f"Sample rate {sr} Hz + short duration ({duration:.1f}s) — common in TTS synthesis."
        elif suspicious_sr:
            score, severity = 0.42, SignalSeverity.MEDIUM
            desc = f"Sample rate {sr} Hz is standard for speech synthesis models (ElevenLabs, Bark, etc.)."
        else:
            score, severity = 0.18, SignalSeverity.LOW
            desc = f"Sample rate {sr} Hz and bitrate {bitrate} bps are consistent with natural audio."

        return score, DetectionSignal(
            name="Audio Format Properties",
            description=desc,
            severity=severity,
            score=score,
            details=f"Duration={duration:.1f}s | SR={sr} Hz | Bitrate={bitrate} bps",
        )
    except Exception as exc:
        return 0.40, DetectionSignal(
            name="Audio Format Error",
            description=str(exc),
            severity=SignalSeverity.LOW,
            score=0.40,
        )


def _audio_spectral_analysis(file_path: Path) -> Tuple[float, DetectionSignal]:
    """
    Frame-level spectral consistency analysis using soundfile + scipy.

    TTS synthesis produces audio with:
      - Unnaturally consistent zero-crossing rate across frames
      - Low variance in short-term energy envelope
      - Abnormally stable spectral centroid

    Natural speech/music varies much more in all three dimensions.
    """
    try:
        import soundfile as sf
        import numpy as np

        data, sr = sf.read(str(file_path), always_2d=False)
        if data.ndim > 1:
            data = data.mean(axis=1)
        data = data.astype(np.float32)
        max_val = np.abs(data).max()
        if max_val > 0:
            data /= max_val

        frame_size = max(int(sr * 0.025), 64)   # 25 ms
        hop_size   = max(int(sr * 0.010), 32)    # 10 ms

        if len(data) < frame_size * 10:
            return 0.38, DetectionSignal(
                name="Audio Spectral Analysis",
                description="Audio too short for spectral analysis.",
                severity=SignalSeverity.LOW,
                score=0.38,
            )

        zcr_vals, energy_vals, centroid_vals = [], [], []
        freqs = np.fft.rfftfreq(frame_size, d=1.0 / sr)

        for i in range(0, len(data) - frame_size, hop_size):
            frame = data[i:i + frame_size]
            # Zero-crossing rate
            zcr_vals.append(float(np.mean(np.diff(np.sign(frame)) != 0)))
            # RMS energy
            energy_vals.append(float(np.sqrt(np.mean(frame ** 2))))
            # Spectral centroid
            mag = np.abs(np.fft.rfft(frame * np.hanning(frame_size)))
            total = mag.sum()
            centroid_vals.append(float((freqs * mag).sum() / (total + 1e-9)))

        def _cv(vals):
            a = np.array(vals)
            return float(a.std() / (a.mean() + 1e-9))

        zcr_cv      = _cv(zcr_vals)
        energy_cv   = _cv(energy_vals)
        centroid_cv = _cv(centroid_vals)

        # Composite consistency score (low = too regular = AI-like)
        consistency = (zcr_cv + energy_cv + centroid_cv) / 3.0

        if consistency < 0.35:
            score, severity = 0.80, SignalSeverity.HIGH
            desc = (
                f"Highly consistent spectral profile (ZCR-CV={zcr_cv:.2f}, "
                f"Energy-CV={energy_cv:.2f}, Centroid-CV={centroid_cv:.2f}). "
                "TTS synthesis produces unnaturally uniform audio dynamics."
            )
        elif consistency < 0.65:
            score, severity = 0.48, SignalSeverity.MEDIUM
            desc = (
                f"Moderately consistent audio (ZCR-CV={zcr_cv:.2f}, "
                f"Energy-CV={energy_cv:.2f}, Centroid-CV={centroid_cv:.2f})."
            )
        else:
            score, severity = 0.15, SignalSeverity.LOW
            desc = (
                f"Natural audio variability (ZCR-CV={zcr_cv:.2f}, "
                f"Energy-CV={energy_cv:.2f}, Centroid-CV={centroid_cv:.2f})."
            )

        return score, DetectionSignal(
            name="Audio Spectral Analysis",
            description=desc,
            severity=severity,
            score=score,
            details=(
                f"ZCR CV={zcr_cv:.3f} | Energy CV={energy_cv:.3f} | "
                f"Centroid CV={centroid_cv:.3f} | Duration={len(data)/sr:.1f}s | SR={sr} Hz"
            ),
        )

    except Exception as exc:
        # soundfile can't read MP3/other compressed formats — fall back gracefully
        return 0.35, DetectionSignal(
            name="Audio Spectral Analysis",
            description=f"Spectral analysis unavailable for this format: {exc}",
            severity=SignalSeverity.LOW,
            score=0.35,
        )


# ─────────────────────────────────────────────────────────────────────────────
# VIDEO HELPERS
# ─────────────────────────────────────────────────────────────────────────────

async def _extract_and_analyze_frame(file_path: Path) -> Tuple[float, List[DetectionSignal]]:
    """Extract first readable JPEG frame from video and run image analysis."""
    try:
        import numpy as np
        from PIL import Image

        with open(file_path, "rb") as f:
            data = f.read(1024 * 1024)

        jpg_start = data.find(b"\xff\xd8\xff")
        if jpg_start != -1:
            jpg_end = data.find(b"\xff\xd9", jpg_start)
            if jpg_end != -1 and jpg_end - jpg_start > 1000:
                frame_data = data[jpg_start:jpg_end + 2]
                img = Image.open(io.BytesIO(frame_data))
                arr = np.array(img.convert("RGB"), dtype=np.float32)
                s_ela,   sig_ela   = _ela_analysis(img)
                s_noise, sig_noise = _noise_analysis(arr)
                s_freq,  sig_freq  = _frequency_analysis(arr)
                prob = s_ela * 0.40 + s_noise * 0.30 + s_freq * 0.30
                return prob, [sig_ela, sig_noise, sig_freq]
    except Exception:
        pass

    return 0.35, [DetectionSignal(
        name="Video Frame Analysis",
        description="Could not extract frames for deep analysis. Metadata-only assessment performed.",
        severity=SignalSeverity.LOW,
        score=0.35,
    )]


def _video_container_check(file_path: Path) -> Tuple[float, DetectionSignal]:
    try:
        with open(file_path, "rb") as f:
            header = f.read(512)

        AI_VIDEO_MARKERS = [b"RunwayML", b"Pika", b"Sora", b"Kling", b"Stable Video"]
        for marker in AI_VIDEO_MARKERS:
            if marker.lower() in header.lower():
                return 0.90, DetectionSignal(
                    name="AI Video Tool Detected",
                    description=f"Container header references known AI video tool: {marker.decode()}",
                    severity=SignalSeverity.HIGH,
                    score=0.90,
                )

        return 0.18, DetectionSignal(
            name="Video Container",
            description="No AI video tool markers found in container header.",
            severity=SignalSeverity.LOW,
            score=0.18,
        )
    except Exception as exc:
        return 0.30, DetectionSignal(
            name="Video Container Check Failed",
            description=str(exc),
            severity=SignalSeverity.LOW,
            score=0.30,
        )
