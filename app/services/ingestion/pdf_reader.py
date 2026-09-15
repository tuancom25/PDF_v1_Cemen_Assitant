from pathlib import Path
import fitz


class PDFReader:
    def __init__(self, pdf_path):
        self.pdf_path = Path(pdf_path)

    def metadata(self):
        with fitz.open(self.pdf_path) as doc:
            return {
                "page_count": len(doc),
                "metadata": doc.metadata or {},
            }

    def iter_pages(self):
        with fitz.open(self.pdf_path) as doc:
            for page_number, page in enumerate(doc, start=1):
                rect = page.rect
                text = page.get_text("text") or ""
                yield {
                    "page": page_number,
                    "width": rect.width,
                    "height": rect.height,
                    "text": text,
                    "text_chars": len(text.strip()),
                    "blocks": page.get_text("blocks"),
                    "image_count": len(page.get_images(full=True)),
                    "drawing_count": len(page.get_drawings()),
                }
