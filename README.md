# PDF Analyzer V1 — Ceme Technical Assistant

Batch analyzer for a 20-book pilot. It preserves document/page/bbox provenance.

Pipeline:
PDF -> PyMuPDF -> page classification -> text or render/OCR -> optional LayoutParser
-> structured page JSON -> manifest -> global report.

Put PDFs in `data/raw/`.

Run:
```bash
python scripts/analyze_pdfs.py --input data/raw --recursive
```

Enable OCR:
```bash
python scripts/analyze_pdfs.py --input data/raw --recursive --ocr
```

Enable LayoutParser:
```bash
python scripts/analyze_pdfs.py --input data/raw --recursive --layout
```

Both:
```bash
python scripts/analyze_pdfs.py --input data/raw --recursive --ocr --layout
```
```bash 
python -m app.services.p_main_2 
```
Important:
- Raw PDFs are never modified.
- Every page keeps source file + page number.
- Text blocks keep PDF bbox.
- OCR records keep bbox + confidence.
- Images and vector objects keep page provenance.
- Each book gets a manifest.json.
- The batch gets data/catalog/global_report.json.

LayoutParser/Detectron2 installation is OS/CUDA dependent, so it is optional at runtime.
