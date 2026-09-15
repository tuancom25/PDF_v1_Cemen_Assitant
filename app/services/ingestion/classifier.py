class PageClassifier:
    def __init__(self, text_chars_threshold=80, scan_image_ratio_threshold=0.55):
        self.text_chars_threshold = text_chars_threshold
        self.scan_image_ratio_threshold = scan_image_ratio_threshold

    def classify(self, page_info):
        chars = page_info["text_chars"]
        images = page_info["image_count"]
        drawings = page_info["drawing_count"]

        if chars >= self.text_chars_threshold:
            if images and drawings:
                return "text_with_image_and_vector"
            if images:
                return "text_with_image"
            if drawings:
                return "text_with_vector"
            return "text"

        if images:
            return "scan_or_image"

        if drawings:
            return "vector_or_drawing"

        return "empty_or_unknown"
