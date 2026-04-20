from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum


class FileType(str, Enum):
    IMAGE = "image"
    DOCUMENT = "document"
    PRESENTATION = "presentation"
    SPREADSHEET = "spreadsheet"
    UNKNOWN = "unknown"


class SignalSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DetectionSignal(BaseModel):
    name: str
    description: str
    severity: SignalSeverity
    score: float  # 0.0–1.0, contribution to AI likelihood
    details: Optional[str] = None


class MetadataField(BaseModel):
    key: str
    value: str
    suspicious: bool = False
    note: Optional[str] = None


class C2PAResult(BaseModel):
    has_credentials: bool
    provider: Optional[str] = None
    claim_generator: Optional[str] = None
    signed: bool = False
    trusted: bool = False
    assertions: List[str] = []
    note: str = ""


class AnalysisResult(BaseModel):
    job_id: str
    filename: str
    file_type: FileType
    file_size_bytes: int
    mime_type: str

    # Core verdict
    ai_probability: float          # 0.0–1.0
    confidence: float              # 0.0–1.0 (how sure we are of the verdict)
    verdict: str                   # "AI-Generated", "Likely AI", "Uncertain", "Likely Authentic", "Authentic"
    verdict_color: str             # "red", "orange", "yellow", "green", "green"

    # Breakdown
    signals: List[DetectionSignal]
    metadata: List[MetadataField]
    c2pa: C2PAResult

    # Sub-scores
    metadata_score: float
    artifact_score: float
    frequency_score: float
    consistency_score: float

    # Context
    analysis_duration_ms: int
    analyzed_at: str

    # Report
    report_available: bool = True
