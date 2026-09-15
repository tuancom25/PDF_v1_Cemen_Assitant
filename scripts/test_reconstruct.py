from pathlib import Path
import json
## -- câu lệnh chạy : python -m scripts.test_reconstruct
##  -- python  ./scripts/test_reconstruct.py > result.txt 2>&1
'''
from app.services.ingestion.models import (
    Page,
    OCRRecord,
    LayoutBlock,
)
'''

from app.services.ingestion.models import (
    OCRRecord,
    LayoutBlock,
    ContentBlock,
    Page,
)
from app.services.ingestion.reconstruct import DocumentReconstructor


def load_page_json_old(path: Path) -> Page:
    """
    Load một Page từ page JSON.
    """

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    ocr_records = [
        OCRRecord(
            text=item["text"],
            polygon=item["polygon"],
            confidence=item.get("confidence"),
        )
        for item in data.get("ocr_records", [])
    ]

    layout_blocks = [
        LayoutBlock(
            index=item["index"],
            type=item["type"],
            score=item.get("score"),
            bbox=tuple(item["bbox"]),
        )
        for item in data.get("layout_blocks", [])
    ]

    return Page(
        document_id=data["document_id"],
        source_file=data["source_file"],
        page=data["page"],
        width=data["width"],
        height=data["height"],
        page_type=data["page_type"],
        text_chars=data.get("text_chars", 0),
        image_count=data.get("image_count", 0),
        drawing_count=data.get("drawing_count", 0),
        native_text=data.get("native_text"),
        text_blocks=data.get("text_blocks", []),
        ocr_records=ocr_records,
        layout_blocks=layout_blocks,
        images=data.get("images", []),
        vector=data.get("vector"),
        ocr_file=data.get("ocr_file"),
        ocr_record_count=data.get(
            "ocr_record_count",
            len(ocr_records),
        ),
        warnings=data.get("warnings", []),
    )


def load_page_json(path: Path) -> Page:
    """
    Load Page metadata + Layout + OCR records
    từ cấu trúc dữ liệu hiện tại của project.
    """

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # -------------------------------------------------
    # Layout
    # -------------------------------------------------

    layout_blocks = [
        LayoutBlock(
            index=item["index"],
            type=item["type"],
            score=item.get("score"),
            bbox=tuple(item["bbox"]),
        )
        for item in data.get("layout", [])
    ]

    # -------------------------------------------------
    # OCR
    # -------------------------------------------------

    ocr_records = []

    ocr_info = data.get("ocr")

    if ocr_info:
        ocr_file = ocr_info.get("file")

        if ocr_file:
            # OCR path trong manifest là relative path
            ocr_path = Path(ocr_file)

            if not ocr_path.is_absolute():
                project_root = path.parents[5]
                ocr_path = project_root / ocr_path

            if not ocr_path.exists():
                raise FileNotFoundError(
                    f"Không tìm thấy OCR file:\n{ocr_path}"
                )

            with ocr_path.open("r", encoding="utf-8") as f:
                ocr_data = json.load(f)

            # Trường hợp OCR JSON là list
            if isinstance(ocr_data, list):
                records_data = ocr_data

            # Trường hợp OCR JSON có wrapper
            elif isinstance(ocr_data, dict):
                records_data = ocr_data.get(
                    "records",
                    ocr_data.get("ocr_records", [])
                )

            else:
                records_data = []

            ocr_records = [
                OCRRecord(
                    text=item["text"],
                    polygon=item["bbox"],
                    confidence=item.get("confidence"),
                )
                for item in records_data
            ]

    # -------------------------------------------------
    # Page
    # -------------------------------------------------

    return Page(
        document_id=data["document_id"],
        source_file=data["source_file"],
        page=data["page"],
        width=data["width"],
        height=data["height"],
        page_type=data["type"],
        text_chars=data.get("text_chars", 0),
        image_count=data.get("image_count", 0),
        drawing_count=data.get("drawing_count", 0),
        text_blocks=data.get("text_blocks", []),
        ocr_records=ocr_records,
        layout_blocks=layout_blocks,
        images=data.get("images", []),
        vector=data.get("vector"),
        ocr_file=(
            data.get("ocr", {}).get("file")
            if data.get("ocr")
            else None
        ),
        ocr_record_count=(
            data.get("ocr", {}).get("record_count", 0)
            if data.get("ocr")
            else 0
        ),
    )

def main():

    print("=" * 70)
    print("TEST RECONSTRUCT")
    print("=" * 70)

    project_root = Path(__file__).resolve().parents[1]

    manifest = (
        project_root
        / "data"
        / "processed"
        / "documents"
        #/ "cement engineers handbook"
        / "1-refa1clinkerburningcoatingformflame-121102035307-phpapp02_2"
        #/ "2004JUN_Variability of NOx Emissions from Precalciner Cement Kiln Systems,_ presented at the 2004 AWMA ann"
        #/ "flameforcementkilnskppradeepkumar-130330054217-phpapp02"
        / "pages"
        #/ "page_0125.json"
        #/ "page_0012.json"
        / "page_0002.json"
        #/ "page_0004.json"
    )

    print(f"JSON : {manifest}")

    if not manifest.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file:\n{manifest}"
        )

    page = load_page_json(manifest)
    text_blocks = page.text_blocks
    print ("================================")
    print ("in dữ liệu text_blocks từ page.text_blocks trước khi reconstruct")
    for i, block in enumerate(text_blocks):
        print(f"Text Block {i}: {block.get('text', '')[:100]}...")

    print()
    print("=" * 70)
    print("PAGE INFORMATION")
    print("=" * 70)

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

    split_x = reconstructor._find_column_split(blocks)
    
    print()
    print("=" * 70)
    print("COLUMN SPLIT")
    print("=" * 70)
    print("Split X:", split_x)

    print(f"Content Blocks : {len(blocks)}")

    print()
    print("=" * 70)
    print ("in dữ liệu text_blocks từ blocks sau  khi reconstruct")
    print("RECONSTRUCTED BLOCKS")
    print("=" * 70)

    total_ocr = 0


    for i, block in enumerate(blocks):
        x1, y1, x2, y2 = block.bbox
        block.reading_order = i 
        print(" -- block " + "-" * 70)
        '''print(
            f"{i:02d} | "
            f"type={block.content_type:<12} | "
            f"x=({x1:.0f},{x2:.0f}) | "
            f"y=({y1:.0f},{y2:.0f}) | "
            f"text={block.text[:50]!r} " 
        )'''
        print(
        f"{block.reading_order:02d} | "
        f"type={block.content_type:<12} | "
        f"x=({block.bbox[0]:.0f},{block.bbox[2]:.0f}) | "
        f"y=({block.bbox[1]:.0f},{block.bbox[3]:.0f}) | "
        f"text='{block.text[:60].replace(chr(10), ' ')}'"
        )
       

    for block in blocks:
        print()
        print("-" * 70)
        print(
        f"{block.block_id} "
        f"x1={block.bbox[0]:.1f} "
        f"x2={block.bbox[2]:.1f}"
       )
        total_ocr += len(block.ocr_records)



        print(f"ORDER       : {block.reading_order}")
        print(f"BLOCK       : {block.block_id}")
        print(f"TYPE        : {block.content_type}")
        print(f"LAYOUT      : {block.layout_index}")
        print(f"LAYOUT SCORE: {block.layout_score}")
        print(f"OCR COUNT   : {len(block.ocr_records)}")
        print(f"CONFIDENCE  : {block.confidence}")
        print(f"BBOX        : {block.bbox}")

        print()
        print("text content: " + block.text)

    print()
    print("=" * 70)
    print("VALIDATION")
    print("=" * 70)

    print(f"Original OCR records : {len(page.ocr_records)}")
    print(f"Reconstructed OCR    : {total_ocr}")

    if total_ocr == len(page.ocr_records):
        print("OK: Không mất OCR record.")
    else:
        print("WARNING: Số OCR record bị thay đổi!")

    orders = [
        block.reading_order
        for block in blocks
    ]

    if orders == list(range(len(blocks))):
        print("OK: reading_order liên tục.")
    else:
        print("WARNING: reading_order không liên tục.")


if __name__ == "__main__":
    main()