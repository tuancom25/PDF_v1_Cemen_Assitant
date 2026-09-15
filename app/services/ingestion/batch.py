import json
from pathlib import Path

from .analyzer import PDFAnalyzerV1
from .config import AnalyzerConfig
from .checkpoint import CheckpointManager


class BatchAnalyzer:

    def __init__(self, config=None):

        self.config = (
            config or AnalyzerConfig()
        )

        self.analyzer = PDFAnalyzerV1(
            self.config
        )

        checkpoint_path = (
            self.config.catalog_root
            / "checkpoint.json"
        )

        self.checkpoint = (
            CheckpointManager(
                checkpoint_path
            )
        )

    def collect_pdfs(
        self,
        input_path,
    ):

        p = Path(input_path)

        if p.is_file():
            return [p]

        return sorted(
            p.glob("*.pdf")
        )

    def run(
        self,
        input_path,
        resume=False,
        force=False,
    ):

        pdfs = self.collect_pdfs(
            input_path
        )

        reports = []

        for i, pdf in enumerate(
            pdfs,
            1
        ):

            document_id = pdf.stem

            print(
                f"[{i}/{len(pdfs)}] "
                f"{pdf.name}"
            )

            # ---------------------------------
            # RESUME
            # ---------------------------------

            if (
                resume
                and not force
                and self.checkpoint.is_completed(
                    document_id
                )
            ):

                print(
                    "    SKIP "
                    "(already completed)"
                )

                continue

            try:

                # ---------------------------------
                # ANALYZE
                # ---------------------------------

                report = (
                    self.analyzer.analyze(
                        pdf,
                        checkpoint=self.checkpoint,
                    )
                )

                reports.append({
                    "document_id":
                        report["document_id"],

                    "status":
                        report["status"],

                    "pages":
                        report["statistics"][
                            "pages"
                        ],

                    "warnings":
                        len(
                            report["warnings"]
                        ),

                    "errors":
                        len(
                            report["errors"]
                        ),
                })

            except Exception as exc:

                print(
                    f"    ERROR: {exc}"
                )

                self.checkpoint.fail_document(
                    document_id,
                    exc,
                )

                reports.append({
                    "document_id":
                        document_id,

                    "status":
                        "failed",

                    "pages": 0,

                    "warnings": 0,

                    "errors": 1,

                    "error": str(exc),
                })

        # ---------------------------------
        # GLOBAL REPORT
        # ---------------------------------

        self.config.catalog_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        report = {
            "documents_found": len(pdfs),
            "documents": reports,
        }

        (
            self.config.catalog_root
            / "global_report.json"
        ).write_text(
            json.dumps(
                report,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        return report