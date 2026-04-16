"""
AI-generated content detection service.

Detection layers (in order of reliability):
  1. ML Neural-Network classifier  — primary signal when available
  2. Forensic heuristics           — corroborating evidence

Weights when ML is available:
  Images    — ML 60 % + heuristics 40 %
  Documents — RoBERTa 15 % + GPT-2 perplexity 20 % + heuristics 65 %
  Audio     — metadata 30 % + format 25 % + spectral 45 %

Weights when ML is NOT available (torch not installed):
  Images    — ELA 28 % + EXIF 18 % + Noise 22 % + Freq 16 % + Color 9 % + Texture 7 %
  Documents — Template 25 % + Buzzwords 22 % + Burstiness 14 % + Vocab 12 % + Phrases 15 % + Para 7 % + Similarity 5 %
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
    """Returns (ai_probability, signals).

    Six-signal pipeline:
      1. AI tool binary/tag scan  — near-definitive when it hits
      2. Metadata completeness     — AI tools skip proper tagging
      3. Format heuristics         — sample rate, duration patterns
      4. Spectral consistency      — ffmpeg-decoded, works on MP3/AAC
      5. Dynamic range             — AI music is hyper-compressed
      6. 30s deep acoustic scan    — spectral flatness, sub-band energy,
                                     envelope smoothness over a full segment
    """
    signals: List[DetectionSignal] = []

    tool_score,     tool_sig     = _audio_ai_tool_scan(file_path)
    meta_score,     meta_sig     = _audio_metadata_check(file_path)
    fmt_score,      fmt_sig      = _audio_format_check(file_path)
    spectral_score, spectral_sig = _audio_spectral_analysis(file_path)
    dynamic_score,  dynamic_sig  = _audio_dynamic_range(file_path)
    deep_score,     deep_sig     = _audio_30s_deep_scan(file_path)

    signals += [tool_sig, meta_sig, fmt_sig, spectral_sig, dynamic_sig, deep_sig]

    if tool_score >= 0.75:
        # AI tool positively identified — use it as primary anchor
        ai_prob = max(
            tool_score * 0.40 + meta_score * 0.12 +
            spectral_score * 0.18 + dynamic_score * 0.15 + deep_score * 0.15,
            0.75,
        )
    else:
        # No tool marker — acoustic signals drive the score entirely.
        # tool_score has a floor of 0.20 (no-match), so give it minimal weight
        # to avoid it dragging down strong acoustic detections.
        ai_prob = (
            meta_score     * 0.18 +
            fmt_score      * 0.10 +
            spectral_score * 0.25 +
            dynamic_score  * 0.22 +
            deep_score     * 0.25
        )
        # Soft boost when tool scan is partial (0.50–0.74)
        if tool_score >= 0.50:
            ai_prob = max(ai_prob, 0.50)

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
    # Try double-newline paragraphs first; fall back to single-newline blocks
    # so structured docs (CVs, reports) that use \n instead of \n\n still work.
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip().split()) > 10]
    if len(paragraphs) < 3:
        # Single-newline fallback for CVs and structured docs (bullet points are shorter)
        paragraphs = [p.strip() for p in text.split("\n") if len(p.strip().split()) > 5]
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
    # Note: terms already in AI_TRANSITIONS are intentionally omitted here
    # to avoid double-counting the same signal across both checks.
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
        "actionable insights",
        "demonstrated ability",
        "dynamic professional", "innovative solutions",
        "strategic thinking", "driving results",
        "holistic approach",
        "leveraging", "value-added", "collaborative environment",
        "attention to detail", "time management",
        "communication skills", "teamwork",
        "go-getter", "outside the box", "think outside",
        "hard-working", "hardworking", "reliable professional",
        "exceed expectations", "above and beyond",
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

# Known AI audio/music generation tool name fragments (lowercase bytes for binary scan)
_AI_AUDIO_TOOL_MARKERS = [
    # Music generation platforms
    b"suno", b"udio", b"stable audio", b"musicgen", b"audiogen",
    b"mubert", b"aiva", b"soundraw", b"boomy", b"loudly",
    b"beatoven", b"riffusion", b"musiclm", b"jukebox", b"musicfy",
    b"soundful", b"ecrett", b"amper",
    # Voice / TTS
    b"elevenlabs", b"eleven labs", b"bark tts", b"vall-e",
    b"tortoisetts", b"coqui", b"playht", b"play.ht",
    b"resemble.ai", b"descript", b"speechify", b"voicify",
    # Generic AI tag markers
    b"generated by ai", b"ai generated", b"ai-generated",
    b"created by ai", b"ai music", b"created with ai",
]


def _audio_ai_tool_scan(file_path: Path) -> Tuple[float, DetectionSignal]:
    """
    Binary scan of the file + full metadata tag scan for known AI
    music / TTS generation tool markers.

    This is the highest-confidence signal: a match is near-definitive.
    """
    found_binary: List[str] = []
    found_tags: List[str] = []

    # ── Binary scan (first 64 KB + last 8 KB) ─────────────────────────────
    try:
        size = file_path.stat().st_size
        with open(file_path, "rb") as f:
            head = f.read(min(65536, size))
            tail = b""
            if size > 65536:
                f.seek(max(0, size - 8192))
                tail = f.read(8192)
        blob = (head + tail).lower()
        for marker in _AI_AUDIO_TOOL_MARKERS:
            if marker in blob:
                found_binary.append(marker.decode("utf-8", errors="ignore"))
    except Exception:
        pass

    # ── Full metadata tag scan ─────────────────────────────────────────────
    try:
        from mutagen import File as MutagenFile
        from app.services.metadata import _flag_software
        audio = MutagenFile(file_path)
        if audio and audio.tags:
            tag_text = " ".join(str(v) for v in audio.tags.values()).lower()
            for marker in _AI_AUDIO_TOOL_MARKERS:
                m = marker.decode("utf-8", errors="ignore")
                if m in tag_text and m not in found_tags:
                    found_tags.append(m)
            # Also run the generic software-flag check on encoder fields
            for k in ("TSSE", "TENC", "encoder", "encoded_by", "comment", "COMM"):
                if k in audio.tags:
                    val = str(audio.tags[k])
                    susp, _note = _flag_software(val)
                    if susp:
                        entry = f"{k}={val[:60]}"
                        if entry not in found_tags:
                            found_tags.append(entry)
    except Exception:
        pass

    all_found = list(dict.fromkeys(found_binary + found_tags))  # deduplicate, keep order

    if all_found:
        score, severity = 0.95, SignalSeverity.HIGH
        desc = (
            f"Known AI audio generation tool detected: {', '.join(all_found[:4])}. "
            "This is a near-definitive indicator of AI-generated audio."
        )
    else:
        score, severity = 0.20, SignalSeverity.LOW
        desc = "No known AI audio generation tool markers found in file binary or metadata."

    return score, DetectionSignal(
        name="AI Audio Tool Detection",
        description=desc,
        severity=severity,
        score=score,
        details=f"Binary hits: {found_binary or 'none'} | Tag hits: {found_tags or 'none'}",
    )


def _audio_metadata_check(file_path: Path) -> Tuple[float, DetectionSignal]:
    """
    Checks metadata *completeness* for a music file.

    AI music platforms typically export tracks with missing or minimal tags
    (no artist, no album, no genre, no year).  A real studio track always
    has at least artist + title.  Missing 3+ of the 5 key fields is a strong
    signal.  Also scans comment/description text for AI-related language.
    """
    try:
        from mutagen import File as MutagenFile
        audio = MutagenFile(file_path)
        if audio is None:
            return 0.55, DetectionSignal(
                name="Audio Metadata",
                description="Could not parse audio file metadata.",
                severity=SignalSeverity.MEDIUM,
                score=0.55,
            )

        if not audio.tags:
            return 0.68, DetectionSignal(
                name="Audio Metadata Absent",
                description=(
                    "No metadata tags found. Professional music always carries at least "
                    "artist and title tags; AI music tools frequently skip tagging."
                ),
                severity=SignalSeverity.HIGH,
                score=0.68,
            )

        tags = audio.tags

        def _has_field(*keys: str) -> bool:
            for k in keys:
                for tag_key in tags.keys():
                    if k.lower() in str(tag_key).lower():
                        val = str(tags[tag_key]).strip()
                        if val and val not in ("", "0", "unknown", "none"):
                            return True
            return False

        has_artist = _has_field("artist", "TPE1", "TPE2", "author")
        has_title  = _has_field("title",  "TIT2", "TIT1")
        has_album  = _has_field("album",  "TALB")
        has_year   = _has_field("year",   "date", "TDRC", "TYER")
        has_genre  = _has_field("genre",  "TCON")

        missing = sum([not has_artist, not has_title, not has_album, not has_year, not has_genre])

        # Scan all tag text for AI-related language
        tag_text = " ".join(str(v) for v in tags.values()).lower()
        ai_lang  = ["generated", "ai ", "artificial", "synthetic", "suno", "udio",
                    "prompt:", "style:", "created with", "instrumental"]
        comment_suspicious = any(p in tag_text for p in ai_lang)

        field_str = (
            f"artist={'✓' if has_artist else '✗'} "
            f"title={'✓' if has_title else '✗'} "
            f"album={'✓' if has_album else '✗'} "
            f"year={'✓' if has_year else '✗'} "
            f"genre={'✓' if has_genre else '✗'}"
        )

        if missing >= 4 or (missing >= 3 and comment_suspicious):
            score, severity = 0.75, SignalSeverity.HIGH
            desc = (
                f"Severely incomplete metadata ({missing}/5 key fields missing). "
                f"{field_str}. AI-generated audio rarely carries full music metadata."
            )
        elif missing >= 3:
            score, severity = 0.58, SignalSeverity.MEDIUM
            desc = f"Incomplete metadata ({missing}/5 fields missing). {field_str}."
        elif missing >= 2 or comment_suspicious:
            score, severity = 0.42, SignalSeverity.MEDIUM
            if comment_suspicious:
                desc = f"Metadata contains AI-related language. {field_str}."
            else:
                desc = f"Partial metadata ({missing}/5 fields missing). {field_str}."
        else:
            score, severity = 0.12, SignalSeverity.LOW
            desc = f"Complete music metadata present. {field_str}."

        return score, DetectionSignal(
            name="Audio Metadata Completeness",
            description=desc,
            severity=severity,
            score=score,
            details=field_str,
        )
    except Exception as exc:
        return 0.40, DetectionSignal(
            name="Audio Metadata Error",
            description=str(exc),
            severity=SignalSeverity.LOW,
            score=0.40,
        )


def _audio_format_check(file_path: Path) -> Tuple[float, DetectionSignal]:
    """
    Format heuristics: sample rate, duration, bitrate, channel count.

    Key insight: TTS tools use 16/22/24 kHz; AI *music* tools (Suno, Udio)
    export at 44100/48000 Hz — so sample rate alone is insufficient.
    We therefore score a combination of factors.
    """
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
        duration = getattr(info, "length",      0)
        bitrate  = getattr(info, "bitrate",     0)
        sr       = getattr(info, "sample_rate", 0)
        channels = getattr(info, "channels",    0)

        suspicion = 0.0
        flags: List[str] = []

        # TTS-typical sample rates
        if sr in (16000, 22050, 24000):
            suspicion += 0.35
            flags.append(f"TTS sample rate ({sr} Hz)")

        # Very short — TTS demo or AI preview
        if 0 < duration < 15:
            suspicion += 0.22
            flags.append(f"Short duration ({duration:.1f}s)")

        # AI generation platforms often cap at exact multiples of 30s / 60s
        if duration > 0 and abs(duration - round(duration)) < 0.08 and round(duration) % 30 == 0:
            suspicion += 0.15
            flags.append(f"Exact duration ({duration:.0f}s — common AI generation limit)")

        # Mono + TTS sample rate
        if channels == 1 and sr in (16000, 22050, 24000):
            suspicion += 0.18
            flags.append("Mono + TTS sample rate")

        score = min(suspicion, 0.85) if flags else 0.15

        if score >= 0.55:
            severity = SignalSeverity.HIGH
            desc = f"Audio format strongly consistent with AI synthesis: {'; '.join(flags)}."
        elif score >= 0.28:
            severity = SignalSeverity.MEDIUM
            desc = f"Suspicious format properties: {'; '.join(flags)}."
        else:
            severity = SignalSeverity.LOW
            desc = (
                f"Normal audio format (SR={sr} Hz, {duration:.1f}s, "
                f"{bitrate // 1000 if bitrate else '?'}kbps). No AI format markers."
            )

        return score, DetectionSignal(
            name="Audio Format Properties",
            description=desc,
            severity=severity,
            score=score,
            details=f"Duration={duration:.1f}s | SR={sr} Hz | Bitrate={bitrate} bps | Channels={channels}",
        )
    except Exception as exc:
        return 0.40, DetectionSignal(
            name="Audio Format Error",
            description=str(exc),
            severity=SignalSeverity.LOW,
            score=0.40,
        )


def _decode_audio_float32(file_path: Path):
    """
    Decode any audio file to float32 mono numpy array.

    Strategy:
      1. Try soundfile (fast; handles WAV, FLAC, OGG but NOT MP3/AAC).
      2. Fall back to ffmpeg subprocess for compressed formats.

    Returns (data: np.ndarray | None, sample_rate: int).
    """
    import numpy as np

    # ── soundfile (fast path) ──────────────────────────────────────────────
    try:
        import soundfile as sf
        data, sr = sf.read(str(file_path), always_2d=False)
        if data.ndim > 1:
            data = data.mean(axis=1)
        return data.astype(np.float32), int(sr)
    except Exception:
        pass

    # ── ffmpeg subprocess (handles MP3, AAC, M4A, …) ──────────────────────
    try:
        import subprocess
        result = subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error",
                "-i", str(file_path),
                "-ac", "1",        # mono
                "-ar", "22050",    # 22 kHz — sufficient for our analysis
                "-f", "f32le",     # raw float32 little-endian PCM
                "pipe:1",
            ],
            capture_output=True,
            timeout=45,
        )
        if result.returncode == 0 and result.stdout:
            data = np.frombuffer(result.stdout, dtype=np.float32).copy()
            return data, 22050
    except Exception:
        pass

    return None, 0


def _audio_spectral_analysis(file_path: Path) -> Tuple[float, DetectionSignal]:
    """
    Frame-level spectral consistency analysis — now works on MP3/AAC via ffmpeg.

    AI-generated audio (both TTS and AI music) tends to exhibit:
      - Unnaturally low variance in zero-crossing rate across frames
      - Very stable short-term energy envelope
      - Abnormally consistent spectral centroid

    Natural recordings vary considerably in all three dimensions.
    """
    import numpy as np

    try:
        data, sr = _decode_audio_float32(file_path)
        if data is None or len(data) == 0:
            return 0.45, DetectionSignal(
                name="Audio Spectral Analysis",
                description="Could not decode audio for spectral analysis.",
                severity=SignalSeverity.LOW,
                score=0.45,
            )

        max_val = np.abs(data).max()
        if max_val > 0:
            data /= max_val

        frame_size = max(int(sr * 0.025), 64)   # 25 ms
        hop_size   = max(int(sr * 0.010), 32)    # 10 ms

        if len(data) < frame_size * 10:
            return 0.40, DetectionSignal(
                name="Audio Spectral Analysis",
                description="Audio too short for spectral analysis.",
                severity=SignalSeverity.LOW,
                score=0.40,
            )

        # Analyse up to 30 s worth of frames for efficiency
        max_frames  = int(30 * sr / hop_size)
        window      = np.hanning(frame_size)
        freqs       = np.fft.rfftfreq(frame_size, d=1.0 / sr)
        zcr_vals, energy_vals, centroid_vals = [], [], []

        frame_count = 0
        for i in range(0, len(data) - frame_size, hop_size):
            if frame_count >= max_frames:
                break
            frame = data[i: i + frame_size]
            zcr_vals.append(float(np.mean(np.diff(np.sign(frame)) != 0)))
            energy_vals.append(float(np.sqrt(np.mean(frame ** 2))))
            mag   = np.abs(np.fft.rfft(frame * window))
            total = mag.sum()
            centroid_vals.append(float((freqs * mag).sum() / (total + 1e-9)))
            frame_count += 1

        def _cv(vals: list) -> float:
            a = np.array(vals)
            return float(a.std() / (a.mean() + 1e-9))

        zcr_cv      = _cv(zcr_vals)
        energy_cv   = _cv(energy_vals)
        centroid_cv = _cv(centroid_vals)
        consistency = (zcr_cv + energy_cv + centroid_cv) / 3.0

        # Tighter thresholds — AI music is more dynamic than TTS but still
        # more homogeneous than organic recordings
        if consistency < 0.30:
            score, severity = 0.85, SignalSeverity.HIGH
            desc = (
                f"Highly consistent spectral profile (composite CV={consistency:.3f}: "
                f"ZCR={zcr_cv:.2f}, Energy={energy_cv:.2f}, Centroid={centroid_cv:.2f}). "
                "AI synthesis produces unnaturally uniform audio dynamics."
            )
        elif consistency < 0.55:
            score, severity = 0.58, SignalSeverity.MEDIUM
            desc = (
                f"Moderately consistent audio profile (composite CV={consistency:.3f}: "
                f"ZCR={zcr_cv:.2f}, Energy={energy_cv:.2f}, Centroid={centroid_cv:.2f})."
            )
        elif consistency < 0.80:
            score, severity = 0.30, SignalSeverity.LOW
            desc = (
                f"Some consistency detected (composite CV={consistency:.3f}) but within "
                "normal range for produced/mastered music."
            )
        else:
            score, severity = 0.12, SignalSeverity.LOW
            desc = (
                f"Natural audio variability (composite CV={consistency:.3f}). "
                "Spectral profile shifts naturally — consistent with organic recording."
            )

        return score, DetectionSignal(
            name="Audio Spectral Analysis",
            description=desc,
            severity=severity,
            score=score,
            details=(
                f"ZCR CV={zcr_cv:.3f} | Energy CV={energy_cv:.3f} | "
                f"Centroid CV={centroid_cv:.3f} | Composite={consistency:.3f} | "
                f"Duration={len(data) / sr:.1f}s | SR={sr} Hz | Frames={frame_count}"
            ),
        )

    except Exception as exc:
        return 0.40, DetectionSignal(
            name="Audio Spectral Analysis",
            description=f"Spectral analysis failed: {exc}",
            severity=SignalSeverity.LOW,
            score=0.40,
        )


def _audio_dynamic_range(file_path: Path) -> Tuple[float, DetectionSignal]:
    """
    Dynamic range analysis — AI music is characteristically over-compressed.

    AI music generation platforms apply aggressive loudness normalisation
    (LUFS targeting), resulting in very low dynamic range and unusually
    consistent RMS levels compared to organic studio recordings (which
    typically span 15–30+ dB of dynamic headroom).
    """
    import numpy as np

    try:
        data, sr = _decode_audio_float32(file_path)
        if data is None or len(data) < sr * 2:
            return 0.40, DetectionSignal(
                name="Dynamic Range Analysis",
                description="Insufficient audio for dynamic range analysis.",
                severity=SignalSeverity.LOW,
                score=0.40,
            )

        # RMS in 500 ms windows with 50 % overlap
        win = max(int(sr * 0.5), 1)
        rms_vals = []
        for i in range(0, len(data) - win, win // 2):
            chunk = data[i: i + win]
            rms = float(np.sqrt(np.mean(chunk ** 2)))
            if rms > 0.001:   # skip near-silence
                rms_vals.append(rms)

        if len(rms_vals) < 4:
            return 0.40, DetectionSignal(
                name="Dynamic Range Analysis",
                description="Audio too short or silent for dynamic range analysis.",
                severity=SignalSeverity.LOW,
                score=0.40,
            )

        rms_arr          = np.array(rms_vals)
        dynamic_range_db = 20 * np.log10(rms_arr.max() / (rms_arr.min() + 1e-9))
        rms_cv           = float(rms_arr.std() / (rms_arr.mean() + 1e-9))

        # Flat / near-silence sections — padding common in AI generation
        total_wins = max(len(data) // (win // 2), 1)
        flat_ratio = (total_wins - len(rms_vals)) / total_wins

        suspicion = 0.0
        flags: List[str] = []

        if dynamic_range_db < 8:
            suspicion += 0.42
            flags.append(f"Very low dynamic range ({dynamic_range_db:.1f} dB)")
        elif dynamic_range_db < 14:
            suspicion += 0.22
            flags.append(f"Low dynamic range ({dynamic_range_db:.1f} dB)")

        if rms_cv < 0.15:
            suspicion += 0.38
            flags.append(f"Hyper-consistent loudness (CV={rms_cv:.3f})")
        elif rms_cv < 0.30:
            suspicion += 0.18
            flags.append(f"Low loudness variation (CV={rms_cv:.3f})")

        if flat_ratio > 0.15:
            suspicion += 0.18
            flags.append(f"High silent-frame ratio ({flat_ratio:.0%})")

        score = min(suspicion, 0.88)

        if score >= 0.55:
            severity = SignalSeverity.HIGH
            desc = f"Hyper-compressed dynamics — hallmark of AI music generation: {'; '.join(flags)}."
        elif score >= 0.28:
            severity = SignalSeverity.MEDIUM
            desc = f"Suspicious dynamic compression: {'; '.join(flags)}." if flags else "Moderately compressed dynamics."
        else:
            severity = SignalSeverity.LOW
            desc = (
                f"Natural dynamic range ({dynamic_range_db:.1f} dB, RMS CV={rms_cv:.3f}). "
                "No unusual compression detected."
            )

        return score, DetectionSignal(
            name="Dynamic Range Analysis",
            description=desc,
            severity=severity,
            score=score,
            details=f"DR={dynamic_range_db:.1f}dB | RMS CV={rms_cv:.3f} | Flat ratio={flat_ratio:.1%}",
        )

    except Exception as exc:
        return 0.35, DetectionSignal(
            name="Dynamic Range Analysis",
            description=f"Dynamic range analysis failed: {exc}",
            severity=SignalSeverity.LOW,
            score=0.35,
        )


def _audio_30s_deep_scan(file_path: Path) -> Tuple[float, DetectionSignal]:
    """
    Deep acoustic analysis over a 30-second segment.

    Extracts 30 s starting at 5 s in (skipping intros/silence) and computes:

    1. Spectral flatness (Wiener entropy) CV — AI synthesis has unnaturally
       stable flatness across frames; natural recordings vary widely.
    2. Sub-band energy CV (bass/mid/high) — AI music maintains suspiciously
       consistent energy distribution across frequency bands over time.
    3. Amplitude envelope CV — AI music loudness barely fluctuates at the
       frame level; real recordings breathe with natural micro-dynamics.

    All three metrics are measured as coefficient of variation (CV = std/mean).
    Low CV across frames = too consistent = AI-like.
    """
    import numpy as np
    import subprocess

    def _extract_segment(path: Path, skip: float, duration: float):
        """Decode `duration` seconds starting at `skip` to float32 mono @ 22050 Hz."""
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-ss", str(skip),
            "-i", str(path),
            "-t", str(duration),
            "-ac", "1",
            "-ar", "22050",
            "-f", "f32le",
            "pipe:1",
        ]
        r = subprocess.run(cmd, capture_output=True, timeout=60)
        if r.returncode == 0 and r.stdout:
            return np.frombuffer(r.stdout, dtype=np.float32).copy()
        return None

    try:
        sr = 22050
        # Try skipping the first 5 s; fall back to start of file
        data = _extract_segment(file_path, skip=5.0, duration=30.0)
        if data is None or len(data) < sr * 5:
            data = _extract_segment(file_path, skip=0.0, duration=30.0)
        if data is None or len(data) < sr * 2:
            return 0.45, DetectionSignal(
                name="30s Deep Acoustic Scan",
                description="Could not extract audio segment for deep analysis.",
                severity=SignalSeverity.LOW,
                score=0.45,
            )

        max_val = np.abs(data).max()
        if max_val > 0:
            data /= max_val

        frame_size = 2048          # ~93 ms @ 22050 Hz — good frequency resolution
        hop_size   = 512           # ~23 ms hop
        window     = np.hanning(frame_size)
        freqs      = np.fft.rfftfreq(frame_size, d=1.0 / sr)

        bass_mask = freqs < 300
        mid_mask  = (freqs >= 300)  & (freqs < 3000)
        high_mask = freqs >= 3000

        flatness_vals: list  = []
        envelope_vals: list  = []
        bass_e: list         = []
        mid_e: list          = []
        high_e: list         = []

        for i in range(0, len(data) - frame_size, hop_size):
            if len(flatness_vals) >= 2000:
                break
            frame = data[i: i + frame_size] * window

            # Amplitude envelope
            envelope_vals.append(float(np.sqrt(np.mean(frame ** 2))))

            mag = np.abs(np.fft.rfft(frame)) + 1e-10

            # Wiener spectral flatness
            log_mean   = float(np.mean(np.log(mag)))
            arith_mean = float(np.mean(mag))
            flatness_vals.append(float(np.exp(log_mean) / (arith_mean + 1e-10)))

            # Sub-band energies
            bass_e.append(float(mag[bass_mask].mean()))
            mid_e.append(float(mag[mid_mask].mean()))
            high_e.append(float(mag[high_mask].mean()))

        def _cv(vals: list) -> float:
            a = np.array(vals)
            m = float(a.mean())
            return float(a.std() / (m + 1e-9)) if m > 0 else 1.0

        envelope_cv   = _cv(envelope_vals)
        flatness_cv   = _cv(flatness_vals)
        bass_cv       = _cv(bass_e)
        mid_cv        = _cv(mid_e)
        high_cv       = _cv(high_e)
        band_cv       = (bass_cv + mid_cv + high_cv) / 3.0
        mean_flatness = float(np.mean(flatness_vals))

        suspicion = 0.0
        flags: List[str] = []

        # Envelope consistency
        if envelope_cv < 0.18:
            suspicion += 0.36
            flags.append(f"hyper-stable loudness envelope (CV={envelope_cv:.3f})")
        elif envelope_cv < 0.35:
            suspicion += 0.16
            flags.append(f"stable loudness envelope (CV={envelope_cv:.3f})")

        # Spectral flatness consistency
        if flatness_cv < 0.08:
            suspicion += 0.32
            flags.append(f"ultra-consistent spectral flatness (CV={flatness_cv:.3f})")
        elif flatness_cv < 0.18:
            suspicion += 0.16
            flags.append(f"consistent spectral flatness (CV={flatness_cv:.3f})")

        # Sub-band energy consistency
        if band_cv < 0.22:
            suspicion += 0.28
            flags.append(f"rigid sub-band energy (CV={band_cv:.3f})")
        elif band_cv < 0.38:
            suspicion += 0.12
            flags.append(f"stable sub-band energy (CV={band_cv:.3f})")

        score = min(suspicion, 0.92)

        if score >= 0.60:
            severity = SignalSeverity.HIGH
            desc = f"30s deep scan: strong AI acoustic signatures — {'; '.join(flags)}."
        elif score >= 0.32:
            severity = SignalSeverity.MEDIUM
            desc = f"30s deep scan: suspicious acoustic patterns — {'; '.join(flags)}."
        else:
            severity = SignalSeverity.LOW
            desc = (
                f"30s deep scan: natural acoustic variation detected "
                f"(envelope CV={envelope_cv:.3f}, flatness CV={flatness_cv:.3f}, "
                f"band CV={band_cv:.3f})."
            )

        return score, DetectionSignal(
            name="30s Deep Acoustic Scan",
            description=desc,
            severity=severity,
            score=score,
            details=(
                f"Envelope CV={envelope_cv:.3f} | Flatness CV={flatness_cv:.3f} | "
                f"Band CV={band_cv:.3f} (bass={bass_cv:.3f} mid={mid_cv:.3f} high={high_cv:.3f}) | "
                f"Mean flatness={mean_flatness:.4f} | Frames={len(flatness_vals)} | SR={sr} Hz"
            ),
        )

    except Exception as exc:
        return 0.40, DetectionSignal(
            name="30s Deep Acoustic Scan",
            description=f"Deep scan failed: {exc}",
            severity=SignalSeverity.LOW,
            score=0.40,
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
