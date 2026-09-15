from pathlib import Path
from app.services.ingestion.loader import DocumentLoader
from app.services.ingestion.reconstruct import DocumentReconstructor

# python -m scripts.test_loader
def main():

    #project_root = Path.cwd()
    project_root = Path(__file__).resolve().parents[1]
    manifest = (
        project_root
        / "data"
        / "processed"
        / "documents"
        #/ "cement engineers handbook"
        / "1-refa1clinkerburningcoatingformflame-121102035307-phpapp02_2"
        / "pages"
        #/ "page_0283.json"   
        #/ "page_0125.json"
        / "page_0002.json"
    )

    loader = DocumentLoader(
        project_root=project_root
    )

    #page = loader.load_page(
    #    manifest
    #)
    page = loader.load_page_json(
        manifest
    )
    print("=" * 70)
    print("PAGE INFORMATION")
    print("=" * 70)

    print(
        "Document :",
        page.document_id
    )

    print(
        "Page     :",
        page.page
    )

    print(
        "Type     :",
        page.page_type
    )

    print(
        "OCR      :",
        len(page.ocr_records)
    )

    print(
        "Layout   :",
        len(page.layout_blocks)
    )

    print()

    print("=" * 70)
    print("LAYOUT")
    print("=" * 70)

    for layout in page.layout_blocks:

        print(
            f"[{layout.index}] "
            f"{layout.type:<10} "
            f"score={layout.score:.3f} "
            f"bbox={layout.bbox}"
        )

    print()

    reconstructor = (
        DocumentReconstructor()
    )

    blocks = (
        reconstructor.reconstruct_page(
            page
        )
    )

    print("=" * 70)
    print("RECONSTRUCTED BLOCKS")
    print("=" * 70)

    for block in blocks:

        print()
        print(
            "-" * 70
        )

        print(
            f"BLOCK      : {block.block_id}"
        )

        print(
            f"TYPE       : {block.content_type}"
        )

        print(
            f"LAYOUT     : {block.layout_index}"
        )

        print(
            f"LAYOUT SCORE: "
            f"{block.layout_score}"
        )

        print(
            f"OCR COUNT  : "
            f"{len(block.ocr_records)}"
        )

        print(
            f"CONFIDENCE : "
            f"{block.confidence:.4f}"
        )

        print(
            f"BBOX       : {block.bbox}"
        )

        print()

        print(block.text)


if __name__ == "__main__":
    main()