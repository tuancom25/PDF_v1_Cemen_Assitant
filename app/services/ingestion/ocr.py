class OCRService:
    def __init__(self, lang="en"):
        try:
            from paddleocr import PaddleOCR
        except ImportError as exc:
            raise RuntimeError(
                "PaddleOCR is not installed or its PaddlePaddle dependency is missing."
            ) from exc

        self.ocr = PaddleOCR(lang=lang, use_angle_cls=False)

    def extract(self, image_path):
        result = self.ocr.ocr(str(image_path), cls=False)
        records = []

        if not result:
            return records

        for line in result[0] or []:
            records.append({
                "text": line[1][0],
                "confidence": float(line[1][1]),
                "bbox": line[0],
            })

        return records
