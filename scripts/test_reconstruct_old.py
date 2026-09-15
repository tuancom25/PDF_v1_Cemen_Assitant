from pathlib import Path

from app.services.ingestion.reconstruct_old_1 import DocumentReconstructor
from app.services.ingestion.models import Page


def load_page_125() -> Page:
    """
    Load page 125 từ file JSON đã có.
    """

    # TODO:
    # Thay path này bằng đúng file page_0125.json của bạn.
    raise NotImplementedError(
        "Chưa cấu hình đường dẫn tới page_0125.json"
    )


def main():
    print("=" * 70)
    print("TEST RECONSTRUCT")
    print("=" * 70)

    page = load_page_125()

    print(f"Document : {page.document_id}")
    print(f"Page     : {page.page}")
    print(f"Type     : {page.page_type}")
    print(f"OCR      : {len(page.ocr_records)}")
    print(f"Layout   : {len(page.layout_blocks)}")

    print()
    print("=" * 70)
    print("RECONSTRUCT")
    print("=" * 70)

    reconstructor = DocumentReconstructor()

    blocks = reconstructor.reconstruct_page(page)

    print(f"Content Blocks : {len(blocks)}")

    print()
    print("=" * 70)
    print("CONTENT BLOCKS")
    print("=" * 70)

    for block in blocks:

        print("-" * 70)

        print(f"ORDER      : {block.reading_order}")
        print(f"BLOCK ID   : {block.block_id}")
        print(f"TYPE       : {block.content_type}")
        print(f"LAYOUT     : {block.layout_index}")
        print(f"LAYOUT SCORE: {block.layout_score}")
        print(f"OCR COUNT  : {len(block.ocr_records)}")
        print(f"CONFIDENCE : {block.confidence}")
        print(f"BBOX       : {block.bbox}")

        print()
        print(block.text)


if __name__ == "__main__":
    main()