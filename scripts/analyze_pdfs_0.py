import argparse

from app.services.ingestion.batch import BatchAnalyzer
from app.services.ingestion.config import AnalyzerConfig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--ocr", action="store_true")
    parser.add_argument("--layout", action="store_true")
    parser.add_argument("--dpi", type=int, default=200)
    args = parser.parse_args()

    config = AnalyzerConfig(
        render_dpi=args.dpi,
        enable_ocr=args.ocr,
        enable_layout=args.layout,
    )

    report = BatchAnalyzer(config).run(
        args.input,
        recursive=args.recursive,
    )

    print("\n=== GLOBAL REPORT ===")
    print(f"Documents: {report['documents_found']}")
    for item in report["documents"]:
        print(
            f"{item['document_id']}: {item['status']} | "
            f"pages={item['pages']} | "
            f"warnings={item['warnings']} | "
            f"errors={item['errors']}"
        )


if __name__ == "__main__":
    main()
