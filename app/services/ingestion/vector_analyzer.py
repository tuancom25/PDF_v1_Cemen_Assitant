import fitz


class VectorAnalyzer:
    def analyze(self, pdf_path, page_number):
        with fitz.open(pdf_path) as doc:
            drawings = doc[page_number - 1].get_drawings()

        items = []
        for index, drawing in enumerate(drawings):
            rect = drawing.get("rect")
            items.append({
                "index": index,
                "bbox": list(rect) if rect else None,
                "item_count": len(drawing.get("items", [])),
            })

        return {"count": len(drawings), "items": items}
