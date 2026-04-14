"""
PDF report generation using ReportLab.
Produces a professional chain-of-custody style evidence report.
"""
import io
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.models.analysis import AnalysisResult, SignalSeverity


def generate_pdf_report(result: AnalysisResult) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    )

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    # ── Colour palette ──
    DARK = colors.HexColor("#0F172A")
    ACCENT = colors.HexColor("#6366F1")
    LIGHT_BG = colors.HexColor("#F8FAFC")
    BORDER = colors.HexColor("#E2E8F0")
    RED = colors.HexColor("#EF4444")
    ORANGE = colors.HexColor("#F97316")
    YELLOW = colors.HexColor("#EAB308")
    GREEN = colors.HexColor("#22C55E")
    MED_GRAY = colors.HexColor("#64748B")

    verdict_colors = {
        "red": RED,
        "orange": ORANGE,
        "yellow": YELLOW,
        "green": GREEN,
    }
    verdict_color = verdict_colors.get(result.verdict_color, ACCENT)

    styles = getSampleStyleSheet()

    def S(name, **kwargs):
        return ParagraphStyle(name, **kwargs)

    title_style = S("Title", fontSize=22, textColor=DARK, spaceAfter=4,
                    fontName="Helvetica-Bold", alignment=TA_LEFT)
    subtitle_style = S("Sub", fontSize=10, textColor=MED_GRAY, spaceAfter=2,
                       fontName="Helvetica", alignment=TA_LEFT)
    section_style = S("Section", fontSize=13, textColor=DARK, spaceBefore=10,
                      spaceAfter=4, fontName="Helvetica-Bold")
    body_style = S("Body", fontSize=9, textColor=DARK, spaceAfter=2,
                   fontName="Helvetica", leading=14)
    small_style = S("Small", fontSize=8, textColor=MED_GRAY, fontName="Helvetica")
    verdict_style = S("Verdict", fontSize=18, textColor=verdict_color,
                      fontName="Helvetica-Bold", alignment=TA_LEFT)
    mono_style = S("Mono", fontSize=8, fontName="Courier", textColor=DARK)

    story = []

    # ── Header ──
    story.append(Paragraph("VeritasAI Forensic Report", title_style))
    story.append(Paragraph("AI-Generated Content Detection &amp; Media Authentication", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=8))

    # ── Report info table ──
    info_data = [
        ["Report ID", result.job_id, "Analyzed", result.analyzed_at[:19].replace("T", " ")],
        ["File", result.filename[:50], "File Type", result.file_type.value.upper()],
        ["File Size", f"{result.file_size_bytes:,} bytes", "MIME Type", result.mime_type],
        ["Analysis Duration", f"{result.analysis_duration_ms} ms", "Tool Version", "VeritasAI v1.0"],
    ]
    info_table = Table(info_data, colWidths=["25%", "30%", "20%", "25%"])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), MED_GRAY),
        ("TEXTCOLOR", (2, 0), (2, -1), MED_GRAY),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_BG, colors.white]),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 8 * mm))

    # ── Verdict section ──
    story.append(Paragraph("VERDICT", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=4))

    verdict_data = [
        [
            Paragraph(f"<b>{result.verdict}</b>", verdict_style),
            "",
            "",
        ],
        [
            Paragraph(f"AI Probability: <b>{result.ai_probability * 100:.1f}%</b>", body_style),
            Paragraph(f"Confidence: <b>{result.confidence * 100:.1f}%</b>", body_style),
            "",
        ],
    ]
    score_bar_data = [
        ["AI Probability Score", f"{result.ai_probability * 100:.1f}%"],
        ["Detection Confidence", f"{result.confidence * 100:.1f}%"],
        ["Metadata Score", f"{result.metadata_score * 100:.1f}%"],
        ["Artifact Score", f"{result.artifact_score * 100:.1f}%"],
        ["Frequency Score", f"{result.frequency_score * 100:.1f}%"],
        ["Consistency Score", f"{result.consistency_score * 100:.1f}%"],
    ]
    score_table = Table(score_bar_data, colWidths=["70%", "30%"])
    score_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
        ("TEXTCOLOR", (1, 0), (1, 0), verdict_color),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_BG, colors.white]),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 6 * mm))

    # ── C2PA Section ──
    story.append(Paragraph("C2PA / CONTENT CREDENTIALS", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=4))

    c2pa = result.c2pa
    c2pa_data = [
        ["Credentials Present", "Yes" if c2pa.has_credentials else "No"],
        ["Provider", c2pa.provider or "—"],
        ["Claim Generator", c2pa.claim_generator or "—"],
        ["Digitally Signed", "Yes" if c2pa.signed else "No"],
        ["Trusted Provider", "Yes" if c2pa.trusted else "No"],
        ["Assertions", ", ".join(c2pa.assertions) if c2pa.assertions else "None"],
        ["Note", c2pa.note],
    ]
    c2pa_table = Table(c2pa_data, colWidths=["35%", "65%"])
    c2pa_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), MED_GRAY),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_BG, colors.white]),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(c2pa_table)
    story.append(Spacer(1, 6 * mm))

    # ── Detection Signals ──
    story.append(Paragraph("DETECTION SIGNALS", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=4))

    severity_colors = {
        SignalSeverity.HIGH: RED,
        SignalSeverity.MEDIUM: ORANGE,
        SignalSeverity.LOW: GREEN,
    }

    signal_header = [
        [
            Paragraph("<b>Signal</b>", small_style),
            Paragraph("<b>Severity</b>", small_style),
            Paragraph("<b>Score</b>", small_style),
            Paragraph("<b>Description</b>", small_style),
        ]
    ]
    signal_rows = []
    for sig in result.signals:
        sc = severity_colors.get(sig.severity, MED_GRAY)
        signal_rows.append([
            Paragraph(sig.name, S("SN", fontSize=8, fontName="Helvetica-Bold")),
            Paragraph(f'<font color="#{_hex(sc)}">{sig.severity.value.upper()}</font>',
                      S("SEV", fontSize=8, fontName="Helvetica-Bold")),
            Paragraph(f"{sig.score * 100:.0f}%", body_style),
            Paragraph(sig.description[:200], body_style),
        ])

    signal_data = signal_header + signal_rows
    signal_table = Table(signal_data, colWidths=["25%", "12%", "8%", "55%"])
    signal_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, colors.white]),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(signal_table)
    story.append(Spacer(1, 6 * mm))

    # ── Metadata ──
    story.append(Paragraph("EXTRACTED METADATA", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=4))

    meta_header = [[
        Paragraph("<b>Field</b>", small_style),
        Paragraph("<b>Value</b>", small_style),
        Paragraph("<b>Suspicious</b>", small_style),
    ]]
    meta_rows = []
    for m in result.metadata:
        flag = "⚠ YES" if m.suspicious else "—"
        note_text = f" ({m.note})" if m.note else ""
        meta_rows.append([
            Paragraph(m.key, S("MK", fontSize=8, fontName="Helvetica-Bold")),
            Paragraph(f"{m.value}{note_text}"[:200], body_style),
            Paragraph(flag, S("MF", fontSize=8, fontName="Helvetica-Bold",
                              textColor=RED if m.suspicious else MED_GRAY)),
        ])

    meta_data = meta_header + meta_rows
    meta_table = Table(meta_data, colWidths=["25%", "60%", "15%"])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, colors.white]),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6 * mm))

    # ── Legal disclaimer ──
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=4))
    story.append(Paragraph(
        "<b>DISCLAIMER:</b> This report is produced by VeritasAI automated forensic analysis. "
        "Results are probabilistic and should not be used as sole evidence in legal proceedings without "
        "additional expert review. Detection accuracy varies by file type, quality, and generation method. "
        "VeritasAI is not liable for decisions made based solely on this report.",
        S("Disc", fontSize=7, textColor=MED_GRAY, fontName="Helvetica", leading=10)
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        f"Generated by VeritasAI v1.0 | {result.analyzed_at[:19].replace('T', ' ')} UTC | "
        f"Job ID: {result.job_id}",
        S("Footer", fontSize=7, textColor=MED_GRAY, fontName="Helvetica", alignment=TA_CENTER)
    ))

    doc.build(story)
    return buf.getvalue()


def _hex(color) -> str:
    """Convert ReportLab color to hex string (without #)."""
    try:
        return "{:02X}{:02X}{:02X}".format(
            int(color.red * 255),
            int(color.green * 255),
            int(color.blue * 255),
        )
    except Exception:
        return "000000"
