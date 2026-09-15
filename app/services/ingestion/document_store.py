import json
from pathlib import Path
#from app.models.document import ( Document, Page, OCRRecord, LayoutBlock ) 
from app.models.document import (
    Document,
    Page,
    OCRRecord,
    LayoutBlock,
)


class DocumentStore:

    def __init__(self, root):
        self.root = Path(root)

    # -------------------------------------------------
    # SAVE
    # -------------------------------------------------

    def save_document(self, document: Document):

        document_dir = self.root / document.document_id
        pages_dir = document_dir / "pages"

        pages_dir.mkdir(parents=True, exist_ok=True)

        # Master / manifest
        manifest = {
            "schema_version": "1.0",
            "document_id": document.document_id,
            "source_file": document.source_file,
            "metadata": document.metadata,
            "page_count": len(document.pages),
        }

        self._write_json(
            document_dir / "manifest.json",
            manifest,
        )

        # Save individual pages
        for page in document.pages:
            self.save_page(document, page)

    # -------------------------------------------------
    # SAVE PAGE
    # -------------------------------------------------

    def save_page(self, document: Document, page: Page):

        document_dir = self.root / document.document_id
        pages_dir = document_dir / "pages"

        pages_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "document_id": document.document_id,

            "page_number": page.page_number,
            "width": page.width,
            "height": page.height,
            "page_type": page.page_type,

            "native_text": page.native_text,

            "text_blocks": page.text_blocks,

            "ocr": [
                {
                    "text": r.text,
                    "bbox": r.bbox,
                    "confidence": r.confidence,
                }
                for r in page.ocr
            ],

            "layout": [
                {
                    "index": b.index,
                    "type": b.type,
                    "score": b.score,
                    "bbox": b.bbox,
                }
                for b in page.layout
            ],

            "images": page.images,
            "vector": page.vector,
        }

        filename = f"page_{page.page_number:04d}.json"

        self._write_json(
            pages_dir / filename,
            data,
        )

    # -------------------------------------------------
    # LOAD
    # -------------------------------------------------

    def load_document(self, document_id: str) -> Document:

        document_dir = self.root / document_id

        manifest_file = document_dir / "manifest.json"

        if not manifest_file.exists():
            raise FileNotFoundError(
                f"Document not found: {document_id}"
            )

        manifest = self._read_json(manifest_file)

        pages = []

        pages_dir = document_dir / "pages"

        for page_file in sorted(
            pages_dir.glob("page_*.json")
        ):
            pages.append(
                self._load_page(page_file)
            )

        return Document(
            document_id=manifest["document_id"],
            source_file=manifest["source_file"],
            metadata=manifest["metadata"],
            pages=pages,
        )

    # -------------------------------------------------
    # LOAD PAGE
    # -------------------------------------------------

    def load_page(
        self,
        document_id: str,
        page_number: int,
    ) -> Page:

        document_dir = self.root / document_id

        filename = f"page_{page_number:04d}.json"

        page_file = (
            document_dir
            / "pages"
            / filename
        )

        if not page_file.exists():
            raise FileNotFoundError(
                f"Page not found: {page_file}"
            )

        return self._load_page(page_file)

    # -------------------------------------------------
    # INTERNAL
    # -------------------------------------------------

    def _load_page(self, page_file: Path) -> Page:

        data = self._read_json(page_file)

        ocr_records = [
            OCRRecord(
                text=r["text"],
                bbox=r["bbox"],
                confidence=r.get("confidence"),
            )
            for r in data.get("ocr", [])
        ]

        layout_blocks = [
            LayoutBlock(
                index=b["index"],
                type=b["type"],
                score=b.get("score"),
                bbox=b["bbox"],
            )
            for b in data.get("layout", [])
        ]

        return Page(
            page_number=data["page_number"],
            width=data["width"],
            height=data["height"],
            page_type=data["page_type"],
            native_text=data.get("native_text"),
            text_blocks=data.get("text_blocks", []),
            ocr=ocr_records,
            layout=layout_blocks,
            images=data.get("images", []),
            vector=data.get("vector"),
        )

    @staticmethod
    def _write_json(path: Path, data):

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _read_json(path: Path):

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )