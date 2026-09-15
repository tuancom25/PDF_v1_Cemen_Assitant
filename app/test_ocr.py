

from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang="vi",
    use_angle_cls=False,
)

print("Running OCR...")

result = ocr.ocr(
    "data/raw/page_0030_image_000.jpeg",
    cls=False
)

print(result)

