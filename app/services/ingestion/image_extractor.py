from pathlib import Path
import fitz


class ImageExtractor:
    def extract(self, pdf_path, page_number, output_dir):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        results = []

        with fitz.open(pdf_path) as doc:
            page = doc[page_number - 1]

            for index, image in enumerate(page.get_images(full=True)):
                xref = image[0]
                data = doc.extract_image(xref)
                ext = data["ext"]
                output_file = output_dir / (
                    f"page_{page_number:04d}_image_{index:03d}.{ext}"
                )
                output_file.write_bytes(data["image"])

                results.append({
                    "index": index,
                    "xref": xref,
                    "file": str(output_file),
                    "width": data.get("width"),
                    "height": data.get("height"),
                    "extension": ext,
                })

        return results
