# Detection Roadmap

This project is strongest when each file type is treated as its own forensic surface rather than being pushed through one generic "AI detector" score.

## Current Priority Order

1. Document package analysis
2. Per-format calibration
3. Better benchmark data
4. Stronger image ensemble
5. UI explanations tied to concrete evidence

## What Is Already Implemented

- DOCX package inspection
  - flags `python-docx` and other generated-by metadata
  - compares internal counters like `Words` and `Paragraphs` against real content
  - parses table-heavy DOCX body text instead of only plain paragraphs
- PDF package inspection
  - checks `/Creator`, `/Producer`, `/Author`, `/Title`
  - flags direct AI or automation markers in PDF metadata
  - inspects page resources for image-only or fontless exports
  - distinguishes text-extractable PDFs from flattened/rasterized exports

## Next Work Items

### 1. PDF Deepening

- inspect XMP metadata streams, not only document-info fields
- extract and score embedded font names, subset patterns, and export chains
- detect page-layout regularity across multi-page guides and reports
- separate "image-only scanned PDF" from "AI-generated designed PDF"

### 2. DOCX Deepening

- inspect `customXml`, comments, tracked changes, headers/footers, numbering, and relationship graphs
- detect templated section reuse across tables and repeated blocks
- inspect embedded images for reuse, compression patterns, and generator metadata

### 3. Image Detector Upgrade

- add a second image model and ensemble it with the current one
- calibrate for `jpg` vs `png` vs `webp`
- split verdicts into:
  - likely AI-generated
  - likely heavily edited
  - likely authentic

### 4. Text Detector Upgrade

- train or fine-tune on structured documents, not only essay-style prose
- add chunk voting for lists, plans, worksheets, and business docs
- add structure-aware features:
  - section repetition
  - cue-template reuse
  - low-entropy instruction blocks
  - repeated layout cadence

### 5. Calibration and Metrics

- build a labeled benchmark set by file type:
  - human DOCX
  - AI-written DOCX
  - human PDF exports
  - AI-generated PDF guides
  - real photos
  - AI images by generator family
- track:
  - precision
  - recall
  - false positive rate
  - false negative rate
- tune thresholds separately for each file type instead of one global scale

### 6. UX / Reporting

- show the top three strongest reasons behind the score
- label signal source by category:
  - metadata
  - package structure
  - text model
  - forensic heuristic
- show when the model score is weak but the package evidence is strong

## Recommended Architecture

- Python for orchestration, ML, scoring, experiments, and reporting
- Rust or C++ only for hotspots:
  - very fast PDF/DOCX parsing
  - native image preprocessing
  - batch-scale forensic feature extraction

## Definition of Done for "Accurate Enough"

The detector should not be considered mature until:

- each major file type has its own package-level parser
- thresholds are calibrated on labeled data
- reports explain the evidence behind high scores
- regression fixtures exist for every previously missed case
