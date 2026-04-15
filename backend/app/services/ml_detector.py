"""
ML-based AI content detection using pre-trained HuggingFace models.

Models used:
  - Image: umm-maybe/AI-image-detector  (ViT fine-tuned on AI vs real images)
  - Text:  Hello-SimpleAI/chatgpt-detector-roberta  (RoBERTa, human vs ChatGPT)
  - Perplexity: openai-community/gpt2  (lower perplexity → more AI-like)

Both models are lazily loaded on first use and kept in memory.
A background preload is triggered on server startup so the first real
request doesn't pay the cold-start penalty.
"""

import logging
import math
import threading
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# ── module-level singletons ──────────────────────────────────────────────────
_image_pipe = None
_text_pipe = None
_gpt2_model = None
_gpt2_tokenizer = None
_image_lock = threading.Lock()
_text_lock = threading.Lock()
_gpt2_lock = threading.Lock()
_torch_available: Optional[bool] = None


def _has_torch() -> bool:
    global _torch_available
    if _torch_available is None:
        try:
            import torch          # noqa: F401
            import transformers   # noqa: F401
            _torch_available = True
        except ImportError:
            _torch_available = False
            logger.warning("torch/transformers not installed — ML detection disabled")
    return _torch_available


# ── model accessors ──────────────────────────────────────────────────────────

def _get_image_pipe():
    global _image_pipe
    if _image_pipe is None:
        with _image_lock:
            if _image_pipe is None:
                from transformers import pipeline
                logger.info("Loading image ML model (umm-maybe/AI-image-detector)…")
                _image_pipe = pipeline(
                    "image-classification",
                    model="umm-maybe/AI-image-detector",
                    device=-1,  # CPU
                )
                logger.info("Image ML model ready")
    return _image_pipe


def _get_text_pipe():
    global _text_pipe
    if _text_pipe is None:
        with _text_lock:
            if _text_pipe is None:
                from transformers import pipeline
                logger.info("Loading text ML model (Hello-SimpleAI/chatgpt-detector-roberta)…")
                _text_pipe = pipeline(
                    "text-classification",
                    model="Hello-SimpleAI/chatgpt-detector-roberta",
                    device=-1,
                    truncation=True,
                    max_length=512,
                )
                logger.info("Text ML model ready")
    return _text_pipe


def _get_gpt2():
    global _gpt2_model, _gpt2_tokenizer
    if _gpt2_model is None:
        with _gpt2_lock:
            if _gpt2_model is None:
                from transformers import GPT2LMHeadModel, GPT2TokenizerFast
                logger.info("Loading GPT-2 perplexity model…")
                _gpt2_tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
                _gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2")
                _gpt2_model.eval()
                logger.info("GPT-2 model ready")
    return _gpt2_model, _gpt2_tokenizer


# ── public API ────────────────────────────────────────────────────────────────

def preload_models() -> None:
    """Fire-and-forget background preload on server startup."""
    if not _has_torch():
        return

    def _load_image():
        try:
            _get_image_pipe()
        except Exception as exc:
            logger.warning("Image model preload failed: %s", exc)

    def _load_text():
        try:
            _get_text_pipe()
        except Exception as exc:
            logger.warning("Text model preload failed: %s", exc)

    def _load_gpt2():
        try:
            _get_gpt2()
        except Exception as exc:
            logger.warning("GPT-2 model preload failed: %s", exc)

    threading.Thread(target=_load_image, daemon=True, name="preload-image-model").start()
    threading.Thread(target=_load_text,  daemon=True, name="preload-text-model").start()
    threading.Thread(target=_load_gpt2,  daemon=True, name="preload-gpt2-model").start()


def ml_image_score(image_path: Path) -> Tuple[Optional[float], str]:
    """
    Run the ViT image classifier.

    Returns:
        (ai_probability, details_string)  — probability is None if unavailable.

    Labels from umm-maybe/AI-image-detector: "artificial" | "human"
    """
    if not _has_torch():
        return None, "ML not available (torch not installed)"

    try:
        from PIL import Image
        pipe = _get_image_pipe()

        img = Image.open(image_path).convert("RGB")
        results = pipe(img)  # list of {"label": str, "score": float}

        score_map = {r["label"].lower(): r["score"] for r in results}
        # "artificial" = AI-generated; "human" = real photo
        ai_prob = score_map.get("artificial", 1.0 - score_map.get("human", 0.5))

        detail_parts = " | ".join(f"{r['label']}: {r['score']:.1%}" for r in results)
        return float(ai_prob), f"ViT classifier — {detail_parts}"

    except Exception as exc:
        logger.warning("ML image score failed: %s", exc)
        return None, str(exc)


def ml_text_score(text: str) -> Tuple[Optional[float], str]:
    """
    Run the RoBERTa text classifier.

    For texts longer than the 512-token limit the text is split into
    overlapping 400-word chunks and the scores are averaged.

    Returns:
        (ai_probability, details_string)  — probability is None if unavailable.

    Labels from Hello-SimpleAI/chatgpt-detector-roberta: "ChatGPT" | "Human"
    """
    if not _has_torch():
        return None, "ML not available (torch not installed)"

    try:
        pipe = _get_text_pipe()
        words = text.split()

        # Build overlapping 400-word chunks, skip very short ones
        chunks: list[str] = []
        step = 350
        for i in range(0, max(1, len(words) - 20), step):
            chunk = " ".join(words[i: i + 450])
            if len(chunk.split()) >= 30:
                chunks.append(chunk)

        if not chunks:
            chunks = [" ".join(words[:450])]

        chunks = chunks[:6]  # cap at 6 chunks (~2700 words)

        ai_scores = []
        for chunk in chunks:
            results = pipe(chunk)
            score_map = {r["label"].lower(): r["score"] for r in results}
            # "chatgpt" = AI; "human" = human
            ai_score = score_map.get("chatgpt", 1.0 - score_map.get("human", 0.5))
            ai_scores.append(ai_score)

        avg = float(sum(ai_scores) / len(ai_scores))
        details = (
            f"RoBERTa classifier — {len(chunks)} chunk(s) analysed | "
            f"Mean AI score: {avg:.1%} | "
            f"Chunk scores: {', '.join(f'{s:.1%}' for s in ai_scores)}"
        )
        return avg, details

    except Exception as exc:
        logger.warning("ML text score failed: %s", exc)
        return None, str(exc)


def ml_perplexity_score(text: str) -> Tuple[Optional[float], str]:
    """
    Compute GPT-2 perplexity on the text.

    AI-generated text is more predictable (lower perplexity under GPT-2)
    than human-written text. Works well even on short, structured text
    where the RoBERTa classifier struggles.

    Returns:
        (ai_probability, details_string)  — probability is None if unavailable.
    """
    if not _has_torch():
        return None, "ML not available (torch not installed)"

    try:
        import torch

        model, tokenizer = _get_gpt2()

        # Flatten bullet-point structure into prose for better perplexity
        clean = " ".join(text.split())
        if len(clean.split()) < 10:
            return None, "Too short for perplexity analysis"

        encodings = tokenizer(
            clean,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        with torch.no_grad():
            outputs = model(**encodings, labels=encodings["input_ids"])
            perplexity = math.exp(min(outputs.loss.item(), 20))  # cap to avoid overflow

        # Calibration (professional/structured text adjusted):
        # AI-generated professional text: typically 15-55 perplexity under GPT-2
        # Human-written professional text: typically 50-150
        if perplexity < 20:
            ai_prob = 0.92
        elif perplexity < 32:
            ai_prob = 0.80
        elif perplexity < 48:
            ai_prob = 0.65
        elif perplexity < 65:
            ai_prob = 0.48
        elif perplexity < 90:
            ai_prob = 0.28
        else:
            ai_prob = 0.10

        return float(ai_prob), f"GPT-2 perplexity={perplexity:.1f} (lower = more AI-like; human text typically >50)"

    except Exception as exc:
        logger.warning("GPT-2 perplexity failed: %s", exc)
        return None, str(exc)
