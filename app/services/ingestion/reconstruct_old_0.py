from typing import Dict, List, Tuple
from typing import Optional

from .models import (
    ContentBlock,
    LayoutBlock,
    OCRRecord,
    Page,
)


class DocumentReconstructor:
    """
    Kết hợp OCR records với Layout blocks.

    V1:
        - spatial matching
        - text reconstruction
        - table reconstruction
        - reading order đơn giản

    Chưa thực hiện:
        - table cell detection
        - row/column reconstruction
        - semantic section detection
    """

    # ---------------------------------------------------------
    # Geometry
    # ---------------------------------------------------------

    @staticmethod
    def _point_inside_bbox(
        point: Tuple[float, float],
        bbox: Tuple[float, float, float, float],
    ) -> bool:

        x, y = point

        x1, y1, x2, y2 = bbox

        return (
            x1 <= x <= x2
            and
            y1 <= y <= y2
        )

    @staticmethod
    def _bbox_area(
        bbox: Tuple[
            float,
            float,
            float,
            float,
        ],
    ) -> float:

        x1, y1, x2, y2 = bbox

        width = max(
            0.0,
            x2 - x1,
        )

        height = max(
            0.0,
            y2 - y1,
        )

        return width * height

    # ---------------------------------------------------------
    # Matching
    # ---------------------------------------------------------

    def _find_layout_for_record(
        self,
        record: OCRRecord,
        layout_blocks: List[LayoutBlock],
    ) -> Optional[LayoutBlock]:

        center = record.center

        candidates = []

        for block in layout_blocks:

            if self._point_inside_bbox(
                center,
                block.bbox,
            ):
                candidates.append(block)

        if not candidates:
            return None

        # Nếu một OCR record nằm trong nhiều bbox,
        # chọn bbox nhỏ nhất.
        #
        # Điều này giúp ưu tiên vùng cụ thể hơn
        # vùng lớn bao quanh nó.

        candidates.sort(
            key=lambda block: self._bbox_area(
                block.bbox
            )
        )

        return candidates[0]

    # ---------------------------------------------------------
    # Reading order
    # ---------------------------------------------------------

    @staticmethod
    def _record_sort_key(
        record: OCRRecord,
    ):

        x1, y1, x2, y2 = record.bbox

        center_x = (x1 + x2) / 2.0
        center_y = (y1 + y2) / 2.0

        return (
            center_y,
            center_x,
        )

    @staticmethod
    def _group_lines(
        records: List[OCRRecord],
        y_tolerance: float = 15.0,
    ) -> List[List[OCRRecord]]:
        """
        Gom OCR records thành các dòng.

        Ví dụ:

        A       B       C

        D       E

        sẽ trở thành:

        [
            [A, B, C],
            [D, E]
        ]
        """

        if not records:
            return []

        records = sorted(
            records,
            key=DocumentReconstructor._record_sort_key,
        )

        lines: List[List[OCRRecord]] = []

        current_line = []

        current_y = None

        for record in records:

            _, y1, _, y2 = record.bbox

            center_y = (
                y1 + y2
            ) / 2.0

            if current_y is None:
                current_line = [
                    record
                ]

                current_y = center_y

                continue

            if abs(
                center_y - current_y
            ) <= y_tolerance:

                current_line.append(
                    record
                )

                # cập nhật trung bình Y
                current_y = (
                    current_y
                    * (len(current_line) - 1)
                    + center_y
                ) / len(current_line)

            else:

                current_line.sort(
                    key=lambda r: r.center[0]
                )

                lines.append(
                    current_line
                )

                current_line = [
                    record
                ]

                current_y = center_y

        if current_line:

            current_line.sort(
                key=lambda r: r.center[0]
            )

            lines.append(
                current_line
            )

        return lines

    # ---------------------------------------------------------
    # Text reconstruction
    # ---------------------------------------------------------

    def _records_to_text(
        self,
        records: List[OCRRecord],
    ) -> str:

        if not records:
            return ""

        lines = self._group_lines(
            records
        )

        text_lines = []

        for line in lines:

            words = []

            for record in line:

                text = record.text.strip()

                if text:
                    words.append(text)

            if words:

                text_lines.append(
                    " ".join(words)
                )

        return "\n".join(
            text_lines
        )

    # ---------------------------------------------------------
    # Confidence
    # ---------------------------------------------------------

    @staticmethod
    def _average_confidence(
        records: List[OCRRecord],
    ) -> float:

        if not records:
            return 0.0

        return sum(
            r.confidence
            for r in records
        ) / len(records)

    # ---------------------------------------------------------
    # Content blocks
    # ---------------------------------------------------------

    def reconstruct_page(
        self,
        page: Page,
    ) -> List[ContentBlock]:

        assignments: Dict[
            int,
            List[OCRRecord]
        ] = {}

        unassigned: List[
            OCRRecord
        ] = []

        # -----------------------------------------------------
        # Assign OCR → Layout
        # -----------------------------------------------------

        for record in page.ocr_records:

            layout = (
                self._find_layout_for_record(
                    record,
                    page.layout_blocks,
                )
            )

            if layout is None:

                unassigned.append(
                    record
                )

                continue

            assignments.setdefault(
                layout.index,
                [],
            ).append(record)

        # -----------------------------------------------------
        # Build ContentBlocks
        # -----------------------------------------------------

        blocks = []

        for layout in page.layout_blocks:

            records = assignments.get(
                layout.index,
                [],
            )

            if not records:
                continue

            text = self._records_to_text(
                records
            )

            confidence = (
                self._average_confidence(
                    records
                )
            )

            block_id = (
                f"{page.document_id}"
                f":p{page.page}"
                f":layout{layout.index}"
            )

            blocks.append(
                ContentBlock(
                    block_id=block_id,
                    content_type=layout.type,
                    page=page.page,
                    text=text,
                    bbox=layout.bbox,
                    confidence=confidence,
                    layout_index=layout.index,
                    layout_score=layout.score,
                    ocr_records=records,
                    metadata={
                        "ocr_record_count": len(
                            records
                        ),
                    },
                )
            )

        # -----------------------------------------------------
        # Unassigned OCR
        # -----------------------------------------------------

        if unassigned:

            text = self._records_to_text(
                unassigned
            )

            confidence = (
                self._average_confidence(
                    unassigned
                )
            )

            # bbox tổng
            bbox = self._calculate_combined_bbox(
                unassigned
            )

            block_id = (
                f"{page.document_id}"
                f":p{page.page}"
                f":unassigned"
            )

            blocks.append(
                ContentBlock(
                    block_id=block_id,
                    content_type="unassigned",
                    page=page.page,
                    text=text,
                    bbox=bbox,
                    confidence=confidence,
                    layout_index=None,
                    layout_score=None,
                    ocr_records=unassigned,
                    metadata={
                        "ocr_record_count": len(
                            unassigned
                        ),
                    },
                )
            )

        # -----------------------------------------------------
        # Reading order của blocks
        # -----------------------------------------------------

        blocks.sort(
            key=lambda block: (
                block.bbox[1],
                block.bbox[0],
            )
        )

        return blocks

    # ---------------------------------------------------------
    # Combined bbox
    # ---------------------------------------------------------

    @staticmethod
    def _calculate_combined_bbox(
        records: List[OCRRecord],
    ):

        if not records:
            return (
                0.0,
                0.0,
                0.0,
                0.0,
            )

        bboxes = [
            record.bbox
            for record in records
        ]

        return (
            min(
                bbox[0]
                for bbox in bboxes
            ),
            min(
                bbox[1]
                for bbox in bboxes
            ),
            max(
                bbox[2]
                for bbox in bboxes
            ),
            max(
                bbox[3]
                for bbox in bboxes
            ),
        )

    # ---------------------------------------------------------
    # Multiple pages
    # ---------------------------------------------------------

    def reconstruct_document(
        self,
        document,
    ) -> Dict[int, List[ContentBlock]]:

        result = {}

        for page in document.pages:

            result[page.page] = (
                self.reconstruct_page(
                    page
                )
            )

        return result