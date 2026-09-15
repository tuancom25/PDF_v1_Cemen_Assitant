import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import (
    Document,
    LayoutBlock,
    OCRRecord,
    Page,
)


class DocumentLoader:
    """
    Load dữ liệu đã được PDF Analyzer tạo ra.

    Input chính:

        page_0283.json

    Sau đó Loader tự đọc:

        ocr/page_0283.json
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path.cwd()

        self.project_root = Path(project_root).resolve()

    # ---------------------------------------------------------
    # JSON
    # ---------------------------------------------------------

    @staticmethod
    def _read_json(path: Path) -> Dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(
                f"Không tìm thấy JSON file: {path}"
            )

        with path.open(
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)

    # ---------------------------------------------------------
    # Path
    # ---------------------------------------------------------

    def _resolve_path(
        self,
        path_string: str,
        base_dir: Path,
    ) -> Path:
        """
        Resolve path được lưu trong JSON.

        Ví dụ JSON:

        data\\processed\\documents\\...
        """

        # Chuẩn hóa Windows separator
        normalized = path_string.replace("\\", "/")

        path = Path(normalized)

        # Nếu là absolute path
        if path.is_absolute():
            return path

        # Thử tương đối với project root
        candidate = self.project_root / path

        if candidate.exists():
            return candidate.resolve()

        # Thử tương đối với thư mục chứa manifest
        candidate = base_dir / path

        if candidate.exists():
            return candidate.resolve()

        # Trả về candidate theo project root
        return (self.project_root / path).resolve()

    # ---------------------------------------------------------
    # OCR
    # ---------------------------------------------------------

    def _load_ocr_records(
        self,
        manifest: Dict[str, Any],
        manifest_path: Path,
    ) -> List[OCRRecord]:

        ocr_info = manifest.get("ocr")

        if not ocr_info:
            return []

        ocr_file = ocr_info.get("file")

        if not ocr_file:
            return []

        ocr_path = self._resolve_path(
            ocr_file,
            manifest_path.parent,
        )

        if not ocr_path.exists():
            raise FileNotFoundError(
                f"Không tìm thấy OCR file: {ocr_path}"
            )

        ocr_data = self._read_json(ocr_path)

        records = []

        for item in ocr_data.get("records", []):
            text = str(
                item.get("text", "")
            ).strip()

            if not text:
                continue

            confidence = float(
                item.get("confidence", 0.0)
            )

            raw_bbox = item.get("bbox", [])

            polygon = []

            for point in raw_bbox:
                if (
                    isinstance(point, list)
                    and len(point) >= 2
                ):
                    polygon.append(
                        (
                            float(point[0]),
                            float(point[1]),
                        )
                    )

            if not polygon:
                continue

            records.append(
                OCRRecord(
                    text=text,
                    confidence=confidence,
                    polygon=polygon,
                )
            )

        return records

    # ---------------------------------------------------------
    # Layout
    # ---------------------------------------------------------

    @staticmethod
    def _load_layout(
        manifest: Dict[str, Any],
    ) -> List[LayoutBlock]:

        result = []

        for item in manifest.get(
            "layout",
            [],
        ):

            bbox = item.get("bbox")

            if not bbox or len(bbox) != 4:
                continue

            result.append(
                LayoutBlock(
                    index=int(
                        item.get(
                            "index",
                            len(result),
                        )
                    ),
                    type=str(
                        item.get(
                            "type",
                            "unknown",
                        )
                    ),
                    score=float(
                        item.get(
                            "score",
                            0.0,
                        )
                    ),
                    bbox=(
                        float(bbox[0]),
                        float(bbox[1]),
                        float(bbox[2]),
                        float(bbox[3]),
                    ),
                )
            )

        return result

    # ---------------------------------------------------------
    # Page
    # ---------------------------------------------------------

    def load_page(
        self,
        manifest_path: Path,
    ) -> Page:

        manifest_path = Path(
            manifest_path
        ).resolve()

        manifest = self._read_json(
            manifest_path
        )

        ocr_records = self._load_ocr_records(
            manifest,
            manifest_path,
        )

        layout_blocks = self._load_layout(
            manifest
        )

        ocr_info = manifest.get(
            "ocr",
            {},
        )

        return Page(
            document_id=str(
                manifest.get(
                    "document_id",
                    "",
                )
            ),
            source_file=str(
                manifest.get(
                    "source_file",
                    "",
                )
            ),
            page=int(
                manifest.get(
                    "page",
                    0,
                )
            ),
            width=float(
                manifest.get(
                    "width",
                    0.0,
                )
            ),
            height=float(
                manifest.get(
                    "height",
                    0.0,
                )
            ),
            page_type=str(
                manifest.get(
                    "type",
                    "unknown",
                )
            ),
            text_chars=int(
                manifest.get(
                    "text_chars",
                    0,
                )
            ),
            image_count=int(
                manifest.get(
                    "image_count",
                    0,
                )
            ),
            drawing_count=int(
                manifest.get(
                    "drawing_count",
                    0,
                )
            ),
            #ocr_file=ocr_info.get(
            #    "file"
            #    if isinstance(ocr_info, dict)
            #    else None
            #),
            # ocr_file=ocr_info.get(
            #              "file"
            #         ) if ocr_info else None
            ocr_file = (
                         ocr_info.get("file")
                         if isinstance(ocr_info, dict)
                         else None
                        ),
            ocr_record_count=int(
                ocr_info.get(
                    "record_count",
                    len(ocr_records),
                ) if isinstance(ocr_info, dict) else len(ocr_records)
            ),
            images=manifest.get(
                "images",
                [],
            ),
            ocr_records=ocr_records,
            layout_blocks=layout_blocks,
            warnings=manifest.get(
                "warnings",
                [],
            ),
        )

    # ---------------------------------------------------------
    # Document
    # ---------------------------------------------------------

    def load_document(
        self,
        manifest_paths: List[Path],
    ) -> Document:

        pages = []

        document_id = ""
        source_file = ""

        for manifest_path in manifest_paths:

            page = self.load_page(
                manifest_path
            )

            pages.append(page)

            if not document_id:
                document_id = page.document_id

            if not source_file:
                source_file = page.source_file

        pages.sort(
            key=lambda p: p.page
        )

        return Document(
            document_id=document_id,
            source_file=source_file,
            pages=pages,
        )

    # ---------------------------------------------------------
    # Directory
    # ---------------------------------------------------------

    def find_page_manifests_old(
        self,
        directory: Path,
    ) -> List[Path]:

        directory = Path(
            directory
        )

        return sorted(
            directory.glob(
                "page_*.json"
            )
        )

    def find_page_manifests(
        self,
        directory: str,
      ) -> List[Path]:

      # pages_dir = directory / "pages"
       directory = Path(directory)
       print("DEBUG directory :", directory)
       print("DEBUG pages_dir :", pages_dir)
       print("DEBUG exists    :", pages_dir.exists())
       print("DEBUG files     :", list(pages_dir.glob("*")))
       pages_dir = directory / "pages"

       print("DEBUG directory :", directory)
       print("DEBUG pages_dir :", pages_dir)
       print("DEBUG exists    :", pages_dir.exists())
       print("DEBUG files     :", list(pages_dir.glob("*")))
       return sorted(
       pages_dir.glob("page_*.json")
       )

    def load_document_directory(
        self,
        directory: Path,
    ) -> Document:

        manifest_paths = (
            self.find_page_manifests(
                directory
            )
        )

        if not manifest_paths:
            raise FileNotFoundError(
                f"Không tìm thấy page_*.json trong: "
                f"{directory}"
            )

        return self.load_document(
            manifest_paths
        )


#---Copy từ test_reconstruct.py
    def load_page_json(self, path: Path) -> Page:
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
