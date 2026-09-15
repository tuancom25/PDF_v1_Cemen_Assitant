import json
from pathlib import Path
from datetime import datetime, timezone
import cv2

from app.services.ingestion import checkpoint

from .classifier import PageClassifier
from .config import AnalyzerConfig
from .image_extractor import ImageExtractor
from .layout_analyzer import LayoutAnalyzer
from .ocr import OCRService
from .page_renderer import PageRenderer
from .pdf_reader import PDFReader
from .vector_analyzer import VectorAnalyzer


class PDFAnalyzerV1:
    def __init__(self, config: AnalyzerConfig):
        self.config = config
        self.classifier = PageClassifier(
            config.text_chars_threshold,
            config.scan_image_ratio_threshold,
        )
        self.renderer = PageRenderer()
        self.images = ImageExtractor()
        self.vectors = VectorAnalyzer()
        #self.ocr = OCRService("en") if config.enable_ocr else None
        self.ocr = OCRService("en") if config.enable_ocr else None
        self.layout = (
            LayoutAnalyzer(
                config.layout_model_config,
                config.layout_score_threshold,
            )
            if config.enable_layout else None
        )

    @staticmethod
    def document_id(pdf_path):
        return Path(pdf_path).stem

    @staticmethod
    def block_bbox(block):
        return [float(x) for x in block[:4]]

    def analyze(self, pdf_path, checkpoint=None,):
        pdf_path = Path(pdf_path)
        doc_id = self.document_id(pdf_path)
        root = self.config.output_root / doc_id

        pages_dir = root / "pages"
        text_dir = root / "text"
        ocr_dir = root / "ocr"
        figure_dir = root / "figures"

        for d in (pages_dir, text_dir, ocr_dir, figure_dir):
            d.mkdir(parents=True, exist_ok=True)

        reader = PDFReader(pdf_path)
        meta = reader.metadata()
        # begin code add
        total_pages = meta["page_count"]
        if checkpoint:

            checkpoint.start_document(
            doc_id,
            total_pages,
            )

            last_page = (
                 checkpoint.last_completed_page(
                 doc_id
           )
        )
        else:
            last_page = 0
        #end code 
        manifest = {
            "schema_version": "1.0",
            "analyzer_version": "PDF Analyzer V1",
            "document_id": doc_id,
            "source": {
                "file_name": pdf_path.name,
                "path": str(pdf_path),
            },
            "metadata": meta["metadata"],
            "started_at": datetime.now(timezone.utc).isoformat(),
            "statistics": {
                "pages": meta["page_count"],
                "text_pages": 0,
                "scan_or_image_pages": 0,
                "vector_pages": 0,
                "pages_with_images": 0,
                "ocr_pages": 0,
                "layout_pages": 0,
            },
            #"pages": [],
            "warnings": [],
            "errors": [],
        }

        for info in reader.iter_pages():
            page_no = info["page"]
            #page_no = info["page"]

            if page_no <= last_page:
               continue
            page_type = self.classifier.classify(info)

            record = {
                "document_id": doc_id,
                "source_file": pdf_path.name,
                "page": page_no,
                "width": info["width"],
                "height": info["height"],
                "type": page_type,
                "text_chars": info["text_chars"],
                "image_count": info["image_count"],
                "drawing_count": info["drawing_count"],
                "text_blocks": [],
                "images": [],
                "vector": None,
                "ocr": None,
                "layout": None,
                "warnings": [],
            }

            for block in info["blocks"]:
                text = block[4] if len(block) > 4 else ""
                if text.strip():
                    record["text_blocks"].append({
                        "bbox": self.block_bbox(block),
                        "text": text,
                    })

            if info["text"].strip():
                (text_dir / f"page_{page_no:04d}.txt").write_text(
                    info["text"], encoding="utf-8"
                )

            if info["image_count"]:
                try:
                    record["images"] = self.images.extract(
                        pdf_path, page_no, figure_dir
                    )
                    manifest["statistics"]["pages_with_images"] += 1
                except Exception as exc:
                    record["warnings"].append(
                        f"image_extraction_failed: {exc}"
                    )

            if info["drawing_count"]:
                try:
                    record["vector"] = self.vectors.analyze(pdf_path, page_no)
                    manifest["statistics"]["vector_pages"] += 1
                except Exception as exc:
                    record["warnings"].append(
                        f"vector_analysis_failed: {exc}"
                    )

            if self.ocr and page_type in {"scan_or_image", "empty_or_unknown"}:
                try:
                    image_file = root / "rendered" / f"page_{page_no:04d}.png"
                    self.renderer.render(
                        pdf_path, page_no, image_file, self.config.render_dpi
                    )
                    records = self.ocr.extract(image_file)
                    ocr_file = ocr_dir / f"page_{page_no:04d}.json"
                    ocr_file.write_text(
                        json.dumps({
                            "document_id": doc_id,
                            "page": page_no,
                            "source_image": str(image_file),
                            "records": records,
                        }, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                    record["ocr"] = {
                        "file": str(ocr_file),
                        "record_count": len(records),
                    }
                    manifest["statistics"]["ocr_pages"] += 1
                except Exception as exc:
                    record["warnings"].append(f"ocr_failed: {exc}")

            if self.layout:
                try:
                    image_file = root / "rendered" / f"page_{page_no:04d}.png"
                    if not image_file.exists():
                        self.renderer.render(
                            pdf_path, page_no, image_file, self.config.render_dpi
                        )

                    image = cv2.imread(str(image_file))
                    if image is None:
                        raise RuntimeError("Could not read rendered page image")

                    record["layout"] = self.layout.detect(image)
                    manifest["statistics"]["layout_pages"] += 1
                except Exception as exc:
                    record["warnings"].append(f"layout_failed: {exc}")

            if page_type == "text":
                manifest["statistics"]["text_pages"] += 1
            elif page_type == "scan_or_image":
                manifest["statistics"]["scan_or_image_pages"] += 1

            page_json = pages_dir / f"page_{page_no:04d}.json"
            page_json.write_text(
                json.dumps(record, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

           # manifest["pages"].append(record)
            manifest["warnings"].extend(
                f"page_{page_no}: {w}" for w in record["warnings"]
            )
            if checkpoint:

                if (
                page_no % 5 == 0
                or page_no == total_pages
                ):

                    checkpoint.update_page(
                        doc_id,
                        page_no,
                    )

        manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
        manifest["status"] = (
            "completed_with_warnings"
            if manifest["warnings"] else "completed"
        )

        (root / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        if checkpoint:

           checkpoint.complete_document(
           doc_id
         )

        return manifest
