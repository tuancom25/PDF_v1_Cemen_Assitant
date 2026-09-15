
from typing import Dict, List, Optional, Tuple
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
    
    # ---------------------------------------------------------
    # Matching
    # ---------------------------------------------------------
    def _find_layout_for_record(
    self,
    record: OCRRecord,
    layout_blocks: List[LayoutBlock],
    threshold: float = 0.30,
    ) -> Optional[LayoutBlock]:

        best_layout = None
        best_ratio = 0.0

        for layout in layout_blocks:
            ratio = self._overlap_ratio(
                record.bbox,
                layout.bbox,
            )

            if ratio > best_ratio:
                best_ratio = ratio
                best_layout = layout

        if best_ratio < threshold:
            return None

        return best_layout
    # ---------------------------------------------------------
    # Reading order
    # ---------------------------------------------------------

    @staticmethod
    def _record_sort_key(
        record: OCRRecord,
    ) -> Tuple[float, float]:

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
    # 
    # ---------------------------------------------------------

    @staticmethod
    def _average_confidence(
        records: List[OCRRecord],
    ) -> Optional[float]:

        values = [
            r.confidence
            for r in records
            if r.confidence is not None
        ]

        if not values:
            return None

        return sum(values) / len(values)

    @staticmethod
    def _find_column_split_old(
        blocks: List[ContentBlock],
        min_gap: float = 100.0,
    ) -> Optional[float]:

        if len(blocks) < 2:
            return None

        x_positions = sorted(
            block.bbox[0]
            for block in blocks
        )

        largest_gap = 0.0
        split_x = None

        for left_x, right_x in zip(
            x_positions,
            x_positions[1:],
        ):
            gap = right_x - left_x

            if gap > largest_gap:
                largest_gap = gap
                split_x = (
                    left_x + right_x
                ) / 2.0

        if largest_gap < min_gap:
            return None

        return split_x
    
    @staticmethod
    def _find_column_split(
        blocks: List[ContentBlock],
        min_gap: float = 200.0,
    ) -> Optional[float]:

        centers = []

        for block in blocks:
            if block.content_type == "unassigned":
                continue

            x1, _, x2, _ = block.bbox
            center_x = (x1 + x2) / 2.0

            centers.append(center_x)

        if len(centers) < 2:
            return None

        centers.sort()

        largest_gap = 0.0
        split_x = None

        for left_x, right_x in zip(
            centers,
            centers[1:],
        ):
            gap = right_x - left_x

            if gap > largest_gap:
                largest_gap = gap
                split_x = (
                    left_x + right_x
                ) / 2.0

        if largest_gap < min_gap:
            return None

        return split_x
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

        # blocks = []
        blocks: List[ContentBlock] = []
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
    )-> Tuple[float, float, float, float]:

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


    
    @staticmethod
    def _intersection_area(
        a: Tuple[float, float, float, float],
        b: Tuple[float, float, float, float],
    ) -> float:

        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b

        x1 = max(ax1, bx1)
        y1 = max(ay1, by1)
        x2 = min(ax2, bx2)
        y2 = min(ay2, by2)

        if x2 <= x1 or y2 <= y1:
            return 0.0

        return (x2 - x1) * (y2 - y1)
   
   
    @staticmethod
    def _overlap_ratio(
        
        ocr_bbox: Tuple[float, float, float, float],
        layout_bbox: Tuple[float, float, float, float],
    ) -> float:

        x1, y1, x2, y2 = ocr_bbox

        ocr_area = max(0.0, x2 - x1) * max(
            0.0,
            y2 - y1,
        )

        if ocr_area <= 0:
            return 0.0

        intersection = DocumentReconstructor._intersection_area(
          ocr_bbox,
          layout_bbox,
        )

        return intersection / ocr_area
