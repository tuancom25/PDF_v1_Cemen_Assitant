class LayoutAnalyzer:
    """
    Layout analyzer based on PaddleOCR PP-StructureV2.

    The public interface is kept compatible with the previous
    LayoutParser/Detectron2 implementation.
    """

    def __init__(self, model_config=None, score_threshold=0.5):
        try:
            from paddleocr import PPStructure
        except ImportError as exc:
            raise RuntimeError(
                "PaddleOCR PP-Structure is not installed."
            ) from exc

        self.score_threshold = score_threshold

        # model_config is kept for backward compatibility with AnalyzerConfig.
        # It is currently not used by PP-Structure.
        self.engine = PPStructure(
            lang="en",
            layout=True,
            table=False,
            ocr=False,
            show_log=False,
        )

    def detect(self, image):
        result = self.engine(image)

        records = []

        if not result:
            return records

        for item in result:
            if not isinstance(item, dict):
                continue

            bbox = item.get("bbox")
            score = item.get("score")
            item_type = item.get("type", "unknown")

            if bbox is None or len(bbox) < 4:
                continue

            # Apply the configured threshold.
            if score is not None and float(score) < self.score_threshold:
                continue

            records.append({
                "index": len(records),
                "type": item_type,
                "score": float(score) if score is not None else None,
                "bbox": [
                    float(bbox[0]),
                    float(bbox[1]),
                    float(bbox[2]),
                    float(bbox[3]),
                ],
            })

        return records