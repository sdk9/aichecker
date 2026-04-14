"""
Metadata extraction service.
Supports images (EXIF), audio, video, PDF, and DOCX files.
"""
import io
import os
import struct
from pathlib import Path
from typing import List, Tuple

from app.models.analysis import MetadataField

# Known AI-generation software strings
AI_SOFTWARE_MARKERS = [
    "midjourney", "dall-e", "dall·e", "stable diffusion", "diffusion",
    "adobe firefly", "generative", "runway", "pika", "kling", "sora",
    "elevenlabs", "whisper", "bark", "audiogen", "musicgen",
    "novelai", "invokeai", "automatic1111", "comfyui", "fooocus",
    "dreamstudio", "nightcafe", "artbreeder",
]

NEUTRAL_SOFTWARE = [
    "adobe photoshop", "lightroom", "capture one", "luminar",
    "gimp", "affinity photo", "darktable", "rawtherapee",
]


def _flag_software(value: str) -> Tuple[bool, str]:
    low = value.lower()
    for marker in AI_SOFTWARE_MARKERS:
        if marker in low:
            return True, f"AI generation tool detected: '{value}'"
    return False, ""


async def extract_metadata(file_path: Path, mime_type: str) -> List[MetadataField]:
    fields: List[MetadataField] = []

    if mime_type.startswith("image/"):
        fields = await _extract_image_metadata(file_path)
    elif mime_type.startswith("audio/"):
        fields = await _extract_audio_metadata(file_path)
    elif mime_type.startswith("video/"):
        fields = await _extract_video_metadata(file_path)
    elif mime_type == "application/pdf":
        fields = await _extract_pdf_metadata(file_path)
    elif mime_type in (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ):
        fields = await _extract_docx_metadata(file_path)

    # Always include basic file stats
    stat = file_path.stat()
    fields.insert(0, MetadataField(key="File Size", value=f"{stat.st_size:,} bytes"))
    fields.insert(1, MetadataField(key="MIME Type", value=mime_type))

    return fields


async def _extract_image_metadata(file_path: Path) -> List[MetadataField]:
    fields: List[MetadataField] = []
    try:
        import exifread
        with open(file_path, "rb") as f:
            tags = exifread.process_file(f, details=False)

        if not tags:
            fields.append(MetadataField(
                key="EXIF Data",
                value="None found",
                suspicious=True,
                note="Missing EXIF is common in AI-generated images; cameras always embed metadata"
            ))
            return fields

        key_map = {
            "Image Make": "Camera Make",
            "Image Model": "Camera Model",
            "Image Software": "Software",
            "EXIF DateTimeOriginal": "Date Taken",
            "EXIF DateTimeDigitized": "Date Digitized",
            "Image DateTime": "Date Modified",
            "EXIF ExposureTime": "Exposure Time",
            "EXIF FNumber": "F-Number",
            "EXIF ISOSpeedRatings": "ISO Speed",
            "EXIF FocalLength": "Focal Length",
            "GPS GPSLatitude": "GPS Latitude",
            "GPS GPSLongitude": "GPS Longitude",
            "Image XResolution": "X Resolution",
            "Image YResolution": "Y Resolution",
            "EXIF ColorSpace": "Color Space",
            "EXIF Flash": "Flash",
            "Image Orientation": "Orientation",
            "EXIF LensModel": "Lens Model",
            "EXIF ExifImageWidth": "Image Width",
            "EXIF ExifImageLength": "Image Height",
        }

        found_camera = False
        found_gps = False

        for exif_key, label in key_map.items():
            if exif_key in tags:
                value = str(tags[exif_key])
                suspicious = False
                note = None

                if label == "Software":
                    suspicious, note = _flag_software(value)
                if label in ("Camera Make", "Camera Model"):
                    found_camera = True
                if label in ("GPS Latitude", "GPS Longitude"):
                    found_gps = True

                fields.append(MetadataField(key=label, value=value, suspicious=suspicious, note=note))

        if not found_camera and tags:
            fields.append(MetadataField(
                key="Camera Hardware",
                value="Not present",
                suspicious=True,
                note="No camera make/model in EXIF — real camera photos always include this"
            ))

    except Exception as e:
        fields.append(MetadataField(key="EXIF Error", value=str(e)))

    # Also try Pillow for image info
    try:
        from PIL import Image
        img = Image.open(file_path)
        fields.append(MetadataField(key="Format", value=img.format or "Unknown"))
        fields.append(MetadataField(key="Mode", value=img.mode))
        fields.append(MetadataField(key="Dimensions", value=f"{img.width} × {img.height} px"))
        if hasattr(img, "info"):
            for k, v in img.info.items():
                if isinstance(v, (str, int, float)) and k.lower() not in ("exif",):
                    label = k.replace("_", " ").title()
                    suspicious, note = _flag_software(str(v)) if "software" in k.lower() or "comment" in k.lower() else (False, None)
                    fields.append(MetadataField(key=label, value=str(v)[:200], suspicious=suspicious, note=note or None))
    except Exception:
        pass

    return fields


async def _extract_audio_metadata(file_path: Path) -> List[MetadataField]:
    fields: List[MetadataField] = []
    try:
        from mutagen import File as MutagenFile
        audio = MutagenFile(file_path)
        if audio is None:
            fields.append(MetadataField(key="Audio Tags", value="None found", suspicious=True))
            return fields

        fields.append(MetadataField(key="Duration", value=f"{audio.info.length:.2f} seconds"))
        if hasattr(audio.info, "bitrate"):
            fields.append(MetadataField(key="Bitrate", value=f"{audio.info.bitrate} bps"))
        if hasattr(audio.info, "sample_rate"):
            fields.append(MetadataField(key="Sample Rate", value=f"{audio.info.sample_rate} Hz"))
        if hasattr(audio.info, "channels"):
            fields.append(MetadataField(key="Channels", value=str(audio.info.channels)))

        tag_map = {
            "TIT2": "Title", "TPE1": "Artist", "TALB": "Album",
            "TYER": "Year", "TENC": "Encoded By", "TSSE": "Encoding Software",
            "COMM": "Comment", "title": "Title", "artist": "Artist",
            "album": "Album", "encoder": "Encoder", "comment": "Comment",
        }
        for tag_key, label in tag_map.items():
            if tag_key in audio:
                value = str(audio[tag_key])
                if hasattr(audio[tag_key], "text"):
                    value = str(audio[tag_key].text[0])
                suspicious, note = _flag_software(value) if label in ("Encoded By", "Encoding Software", "Encoder") else (False, None)
                fields.append(MetadataField(key=label, value=value[:200], suspicious=suspicious, note=note or None))

        if not any(f.key in ("Title", "Artist", "Encoded By") for f in fields):
            fields.append(MetadataField(
                key="Audio Tags",
                value="Minimal metadata",
                suspicious=True,
                note="Synthetic audio often lacks standard tagging"
            ))
    except Exception as e:
        fields.append(MetadataField(key="Audio Metadata Error", value=str(e)))
    return fields


async def _extract_video_metadata(file_path: Path) -> List[MetadataField]:
    fields: List[MetadataField] = []
    # Basic container parse without ffprobe dependency
    try:
        size = file_path.stat().st_size
        fields.append(MetadataField(key="File Size", value=f"{size:,} bytes"))

        suffix = file_path.suffix.lower()
        if suffix == ".mp4":
            fields.extend(await _parse_mp4_metadata(file_path))
        else:
            fields.append(MetadataField(
                key="Video Container",
                value=suffix.lstrip(".").upper(),
                suspicious=False
            ))
    except Exception as e:
        fields.append(MetadataField(key="Video Metadata Error", value=str(e)))
    return fields


async def _parse_mp4_metadata(file_path: Path) -> List[MetadataField]:
    """Minimal MP4 box parser to extract creation time and encoder."""
    fields: List[MetadataField] = []
    try:
        with open(file_path, "rb") as f:
            data = f.read(min(65536, file_path.stat().st_size))

        # Look for 'ftyp' box brand
        idx = data.find(b"ftyp")
        if idx >= 4:
            brand = data[idx + 4:idx + 8].decode("ascii", errors="replace").strip()
            fields.append(MetadataField(key="MP4 Brand", value=brand))

        # Look for encoder string heuristically
        for marker in [b"\xa9too", b"\xa9swr", b"Encoder", b"encoder"]:
            idx = data.find(marker)
            if idx != -1:
                snippet = data[idx + len(marker):idx + len(marker) + 80]
                text = snippet.decode("utf-8", errors="replace").split("\x00")[0].strip()
                if text:
                    suspicious, note = _flag_software(text)
                    fields.append(MetadataField(key="Encoder", value=text, suspicious=suspicious, note=note or None))
                    break

    except Exception:
        pass
    return fields


async def _extract_pdf_metadata(file_path: Path) -> List[MetadataField]:
    fields: List[MetadataField] = []
    try:
        import PyPDF2
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            info = reader.metadata
            num_pages = len(reader.pages)

        fields.append(MetadataField(key="Page Count", value=str(num_pages)))

        if info:
            meta_map = {
                "/Title": "Title",
                "/Author": "Author",
                "/Creator": "Creator",
                "/Producer": "Producer",
                "/CreationDate": "Created",
                "/ModDate": "Modified",
                "/Subject": "Subject",
                "/Keywords": "Keywords",
            }
            for pdf_key, label in meta_map.items():
                if pdf_key in info and info[pdf_key]:
                    value = str(info[pdf_key])
                    suspicious, note = _flag_software(value) if label in ("Creator", "Producer") else (False, None)
                    fields.append(MetadataField(key=label, value=value[:300], suspicious=suspicious, note=note or None))
        else:
            fields.append(MetadataField(
                key="PDF Metadata",
                value="None found",
                suspicious=True,
                note="Documents without author/creator metadata are unusual"
            ))
    except Exception as e:
        fields.append(MetadataField(key="PDF Error", value=str(e)))
    return fields


async def _extract_docx_metadata(file_path: Path) -> List[MetadataField]:
    fields: List[MetadataField] = []
    try:
        from docx import Document
        doc = Document(file_path)
        core = doc.core_properties

        prop_map = [
            ("Author", core.author),
            ("Title", core.title),
            ("Subject", core.subject),
            ("Keywords", core.keywords),
            ("Created", str(core.created) if core.created else None),
            ("Modified", str(core.modified) if core.modified else None),
            ("Last Modified By", core.last_modified_by),
            ("Revision", str(core.revision) if core.revision else None),
            ("Category", core.category),
            ("Comments", core.comments),
        ]

        for label, value in prop_map:
            if value:
                suspicious, note = _flag_software(value) if label in ("Comments", "Keywords") else (False, None)
                fields.append(MetadataField(key=label, value=str(value)[:300], suspicious=suspicious, note=note or None))

        fields.append(MetadataField(key="Paragraph Count", value=str(len(doc.paragraphs))))

        if not core.author and not core.last_modified_by:
            fields.append(MetadataField(
                key="Authorship",
                value="No author metadata",
                suspicious=True,
                note="Documents stripped of author info may have been generated or sanitized"
            ))

    except Exception as e:
        fields.append(MetadataField(key="DOCX Error", value=str(e)))
    return fields
