# Pilot 20 books

## Phase 1 — PDF structure only

```bash
python scripts/analyze_pdfs.py --input data/raw --recursive
```

Inspect:
- page count
- text/scan/vector distribution
- images
- per-page JSON
- manifest
- global_report.json

## Phase 2 — OCR

```bash
python scripts/analyze_pdfs.py --input data/raw --recursive --ocr
```

## Phase 3 — LayoutParser

```bash
python scripts/analyze_pdfs.py --input data/raw --recursive --ocr --layout
```

Không nên bật mọi thứ ngay lần đầu. Mục tiêu của pilot là tìm lỗi và đo chi phí
từng tầng.

## Expected output

```text
data/processed/documents/book_001/
    manifest.json
    pages/page_0001.json
    text/page_0001.txt
    ocr/page_0007.json
    figures/page_0012_image_000.png

data/catalog/global_report.json
```
