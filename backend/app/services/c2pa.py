"""
C2PA (Coalition for Content Provenance and Authenticity) / Content Credentials checker.
Looks for C2PA manifests embedded in JPEG, PNG, WEBP, and MP4 files.
"""
import struct
from pathlib import Path
from typing import Optional

from app.models.analysis import C2PAResult

# C2PA JUMBF box identifier
C2PA_JUMBF_LABEL = b"c2pa"
C2PA_XMP_MARKER = b"http://c2pa.org"
C2PA_CLAIM_GENERATOR_KEY = b"claim_generator"

# Known trusted C2PA providers
TRUSTED_PROVIDERS = [
    "adobe", "microsoft", "google", "truepic", "leica", "sony", "nikon", "canon",
    "reuters", "ap content services", "bbc", "associated press",
]


async def check_c2pa(file_path: Path, mime_type: str) -> C2PAResult:
    """
    Parse the file binary for C2PA / Content Credentials markers.
    Returns a C2PAResult with findings.
    """
    try:
        with open(file_path, "rb") as f:
            data = f.read()
    except Exception as e:
        return C2PAResult(
            has_credentials=False,
            note=f"Could not read file: {e}"
        )

    # Check for C2PA JUMBF box
    has_jumbf = C2PA_JUMBF_LABEL in data
    has_xmp = C2PA_XMP_MARKER in data

    if not has_jumbf and not has_xmp:
        return C2PAResult(
            has_credentials=False,
            note="No C2PA Content Credentials found. File has no provenance record."
        )

    # Try to extract claim generator and provider
    claim_generator = _extract_string_near(data, b"claim_generator", 200)
    provider = _extract_string_near(data, b"\"alg\"", 100) or _extract_string_near(data, b"issuer", 150)

    # Check for signing certificate marker
    signed = b"x5chain" in data or b"\"sig\"" in data

    # Heuristic trust check
    trusted = False
    if claim_generator:
        low = claim_generator.lower()
        trusted = any(tp in low for tp in TRUSTED_PROVIDERS)

    assertions = []
    if b"c2pa.actions" in data:
        assertions.append("c2pa.actions")
    if b"c2pa.hash.data" in data:
        assertions.append("c2pa.hash.data")
    if b"c2pa.thumbnail" in data:
        assertions.append("c2pa.thumbnail")
    if b"stds.schema-org.CreativeWork" in data:
        assertions.append("stds.schema-org.CreativeWork")
    if b"c2pa.ai_generative_training" in data:
        assertions.append("c2pa.ai_generative_training")
    if b"c2pa.training-mining" in data:
        assertions.append("c2pa.training-mining")

    note = "C2PA Content Credentials present."
    if signed and trusted:
        note += " Signed by a trusted provider."
    elif signed:
        note += " Signed but provider not in trusted list."
    else:
        note += " Not digitally signed — credentials may be self-asserted."

    return C2PAResult(
        has_credentials=True,
        provider=provider or "Unknown",
        claim_generator=claim_generator or "Unknown",
        signed=signed,
        trusted=trusted,
        assertions=assertions,
        note=note,
    )


def _extract_string_near(data: bytes, marker: bytes, length: int) -> Optional[str]:
    """Find marker in bytes and extract a printable string nearby."""
    idx = data.find(marker)
    if idx == -1:
        return None
    snippet = data[idx + len(marker): idx + len(marker) + length]
    # Extract printable ASCII
    result = ""
    reading = False
    for b in snippet:
        ch = chr(b)
        if ch in ('"', "'", ":", " "):
            if result:
                break
            continue
        if 32 <= b < 127:
            reading = True
            result += ch
        elif reading:
            break
    return result.strip(' "/') if result else None
