from pathlib import Path
import fitz


class PageRenderer:
    def render(self, pdf_path, page_number, output_file, dpi=200):
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with fitz.open(pdf_path) as doc:
            pix = doc[page_number - 1].get_pixmap(dpi=dpi, alpha=False)
            pix.save(str(output_file))

        return output_file
