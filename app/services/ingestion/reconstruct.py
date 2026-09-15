
from typing import Dict, List, Optional, Tuple

from .models import (
    ContentBlock,
    LayoutBlock,
    OCRRecord,
    Page,
)


class DocumentReconstructor:
    """
    Reconstruct Page -> ContentBlock.

    Kiến trúc:

        Page
         |
         +---- Native Text
         |
         +---- OCR
         |
         +---- Layout / Figure / Vector
                    |
                    v
                  MERGE
                    |
                    v
              Reading Order
                    |
                    v
              ContentBlocks

    Nguyên tắc:

    1. OCR không phải điều kiện bắt buộc.
    2. Native text có thể tự tạo ContentBlock.
    3. Layout có thể tạo ContentBlock cho figure/vector.
    4. OCR có thể bổ sung text vào Layout block.
    5. OCR không match Layout được đưa vào unassigned ContentBlock.
    6. Cuối cùng tất cả block được merge và sắp xếp reading order.
    """

    # =========================================================
    # Geometry
    # =========================================================

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
        source_bbox: Tuple[float, float, float, float],
        target_bbox: Tuple[float, float, float, float],
    ) -> float:

        x1, y1, x2, y2 = source_bbox

        source_area = (
            max(0.0, x2 - x1)
            * max(0.0, y2 - y1)
        )

        if source_area <= 0:
            return 0.0

        intersection = (
            DocumentReconstructor._intersection_area(
                source_bbox,
                target_bbox,
            )
        )

        return intersection / source_area

    # =========================================================
    # OCR -> Layout matching
    # =========================================================

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

    # =========================================================
    # Reading order
    # =========================================================

    @staticmethod
    def _block_sort_key(
        block: ContentBlock,
    ) -> Tuple[float, float]:

        x1, y1, x2, y2 = block.bbox

        return (
            y1,
            x1,
        )

    # =========================================================
    # OCR reading order
    # =========================================================

    @staticmethod
    def _record_sort_key(
        record: OCRRecord,
    ) -> Tuple[float, float]:

        x1, y1, x2, y2 = record.bbox

        center_x = (
            x1 + x2
        ) / 2.0

        center_y = (
            y1 + y2
        ) / 2.0

        return (
            center_y,
            center_x,
        )

    @staticmethod
    def _group_lines(
        records: List[OCRRecord],
        y_tolerance: float = 15.0,
    ) -> List[List[OCRRecord]]:

        if not records:
            return []

        records = sorted(
            records,
            key=DocumentReconstructor._record_sort_key,
        )

        lines: List[List[OCRRecord]] = []

        current_line: List[OCRRecord] = []

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

    @staticmethod
    def _records_to_text(
        records: List[OCRRecord],
    ) -> str:

        if not records:
            return ""

        lines = (
            DocumentReconstructor._group_lines(
                records
            )
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

    # =========================================================
    # Confidence
    # =========================================================

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

    # =========================================================
    # Native Text branch
    # =========================================================

    def _reconstruct_native_text(
        self,
        page: Page,
    ) -> List[ContentBlock]:

        """
        NHÁNH 1

        Native PDF text -> ContentBlock.

        Vì model Page hiện tại có thể chưa cố định tên
        field native text, hàm này thử các field phổ biến.

        Nếu chưa có native text thì trả [].

        Sau khi xác nhận models.py, nên chuẩn hóa
        Page.native_text_blocks thành một field duy nhất.
        """

        blocks: List[ContentBlock] = []

        native_records = None

        # ---------------------------------------------
        # Các khả năng field hiện tại
        # ---------------------------------------------
        print (" ===== kiểm tra native text records trong Reconstruct ===== ")
        native_records =[]
        if hasattr(page, "text_blocks"):
            native_records = page.text_blocks
            #print (f"Found text_blocks: {len(native_records)}")
            native_records
        elif hasattr(page, "text_records"):
            native_records = page.text_records

        elif hasattr(page, "native_text_blocks"):
            native_records = page.native_text_blocks

        # Không có native text
        if not native_records:
            return blocks

        # ---------------------------------------------
        # Mỗi native record -> ContentBlock
        # ---------------------------------------------
        block_index_prefix = 0 
        print (" ===== hien thị native text records ===== ")
        for index, record in enumerate(native_records):
            
            text = getattr(
                record,
                "text",
                "",
            )
            #if text is None:
           # print ("XXXX ::text = "+ text)
            text = record["text"]
           # text_blocks = record.text
           # print (f"Native record {index}: text length = {len(text)}")
           # print (f"Native record {index}: text = {text[:50]}")  # Print first 50 characters
           # print (f"Native record {index}: text_blocks = {text_blocks[:50]}...")
            print (f"Native record {index}: text = {record['text']} ")  # Print first 50 characters
            bbox = getattr(
                record,
                "bbox",
                None,
            )
            if bbox is None:
               bbox = record["bbox"]

            #if not text or bbox is None:
            #   print (f"Skipping native record {index} due to missing text or bbox.")
            #   continue
            

            block_id = (
                f"{page.document_id}"
                f":p{page.page}"
                f":native{index}"
            )

            blocks.append(
                ContentBlock(
                    block_id=block_id,
                    content_type="text",
                    page=page.page,
                    text=text.strip(),
                    bbox=bbox,
                    confidence=None,
                    layout_index=None,
                    layout_score=None,
                    ocr_records=[],
                    metadata={
                        "source": "native_text",
                    },
                )
            )
        '''
        print (" ====******  hien thị native text records sau khi tạo ContentBlock ===== ")
        for block in blocks:
            print (f"Native block: {block.block_id}, text length = {len(block.text)}")
            print (f"Native block: {block.block_id}, text = {block.text[:50]}...")  # Print first 50 characters
        '''
        return blocks

    # =========================================================
    # OCR branch
    # =========================================================

    def _reconstruct_ocr(
        self,
        page: Page,
    ) -> Tuple[
        Dict[int, List[OCRRecord]],
        List[OCRRecord],
    ]:

        """
        NHÁNH 2

        OCR độc lập.

        Kết quả:

            assignments
                layout_index -> OCR records

            unassigned
                OCR records không match Layout
        """

        assignments: Dict[
            int,
            List[OCRRecord],
        ] = {}

        unassigned: List[
            OCRRecord
        ] = []

        # ---------------------------------------------
        # Không có OCR -> hoàn toàn hợp lệ
        # ---------------------------------------------

        if not page.ocr_records:

            return (
                assignments,
                unassigned,
            )

        # ---------------------------------------------
        # OCR -> Layout
        # ---------------------------------------------

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

        return (
            assignments,
            unassigned,
        )

    # =========================================================
    # Layout branch
    # =========================================================

    def _reconstruct_layout(
        self,
        page: Page,
        assignments: Dict[
            int,
            List[OCRRecord],
        ],
    ) -> List[ContentBlock]:

        """
        NHÁNH 3

        Layout độc lập.

        Rất quan trọng:

        Layout block KHÔNG cần OCR để tồn tại.

        Ví dụ:

            OCR = 0
            Layout = 2

        vẫn phải có khả năng tạo ContentBlock.
        """

        blocks: List[ContentBlock] = []

        for layout in page.layout_blocks:

            records = assignments.get(
                layout.index,
                [],
            )

            # -----------------------------------------
            # Có OCR
            # -----------------------------------------

            if records:

                text = (
                    self._records_to_text(
                        records
                    )
                )

                confidence = (
                    self._average_confidence(
                        records
                    )
                )

                source = "ocr_layout"

            # -----------------------------------------
            # Không có OCR
            #
            # Layout vẫn tồn tại.
            # -----------------------------------------

            else:

                text = ""

                confidence = None

                source = "layout_only"

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
                        "source": source,
                        "ocr_record_count": len(
                            records
                        ),
                    },
                )
            )

        return blocks

    # =========================================================
    # Unassigned OCR
    # =========================================================

    def _build_unassigned_block(
        self,
        page: Page,
        records: List[OCRRecord],
    ) -> Optional[ContentBlock]:

        """
        OCR không match Layout.

        Không làm mất OCR data.
        """

        if not records:
            return None

        text = (
            self._records_to_text(
                records
            )
        )

        confidence = (
            self._average_confidence(
                records
            )
        )

        bbox = (
            self._calculate_combined_bbox(
                records
            )
        )

        block_id = (
            f"{page.document_id}"
            f":p{page.page}"
            f":unassigned"
        )

        return ContentBlock(
            block_id=block_id,
            content_type="unassigned",
            page=page.page,
            text=text,
            bbox=bbox,
            confidence=confidence,
            layout_index=None,
            layout_score=None,
            ocr_records=records,
            metadata={
                "source": "ocr_unassigned",
                "ocr_record_count": len(
                    records
                ),
            },
        )

    # =========================================================
    # MERGE
    # =========================================================

    def _merge_blocks(
        self,
        native_blocks: List[ContentBlock],
        layout_blocks: List[ContentBlock],
        unassigned_blocks: List[ContentBlock],
    ) -> List[ContentBlock]:

        """
        Gộp ba nguồn:

            Native
            Layout
            Unassigned OCR

        thành một danh sách ContentBlock.
        """

        blocks: List[ContentBlock] = []

        blocks.extend(
            native_blocks
        )
       # print ("^^^^^^**** dữ liệu text_blocks  trong hàm _merge_blocks trước khi extend layout_blocks")
        #for block in blocks:
        #    print (f"Native block: {block.block_id}, text length = {len(block.text)}")
        #    print (f"Native block: {block.block_id}, text = {block.text[:50]}...")  # Print first 50 characters
        blocks.extend(
            layout_blocks
        )

        blocks.extend(
            unassigned_blocks
        )

        # ---------------------------------------------
        # Reading order
        # ---------------------------------------------

        blocks.sort(
            key=self._block_sort_key
        )

        # ---------------------------------------------
        # Chuẩn hóa index
        # ---------------------------------------------

        for index, block in enumerate(
            blocks
        ):

            # ContentBlock của project hiện tại
            # không nhất thiết có field index.
            #
            # Nếu model có index thì cập nhật.
            block.block_index = index
            if hasattr(block, "index"):

                try:
                    block.index = index
                except Exception:
                    pass

            if hasattr(block, "metadata"):

                block.metadata[
                    "reading_order"
                ] = index
            
        return blocks


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

    # =========================================================
    # MAIN PAGE RECONSTRUCTION
    # =========================================================
    
    def reconstruct_page(
        self,
        page: Page,
    ) -> List[ContentBlock]:

        """
        Pipeline chính:

            1. Native Text
            2. OCR
            3. Layout
            4. Unassigned OCR
            5. Merge
            6. Reading Order
        """

        # =====================================================
        # 1. NATIVE TEXT
        # =====================================================

        native_blocks = (
            self._reconstruct_native_text(
                page
            )
        )

        # =====================================================
        # 2. OCR
        # =====================================================

        (
            assignments,
            unassigned,
        ) = self._reconstruct_ocr(
            page
        )

        # =====================================================
        # 3. LAYOUT
        # =====================================================

        layout_content_blocks = (
            self._reconstruct_layout(
                page,
                assignments,
            )
        )

        # =====================================================
        # 4. UNASSIGNED OCR
        # =====================================================

        unassigned_block = (
            self._build_unassigned_block(
                page,
                unassigned,
            )
        )

        unassigned_blocks = []

        if unassigned_block is not None:

            unassigned_blocks.append(
                unassigned_block
            )

        # =====================================================
        # 5. MERGE
        # =====================================================

        blocks = self._merge_blocks(
            native_blocks=native_blocks,
            layout_blocks=layout_content_blocks,
            unassigned_blocks=unassigned_blocks,
        )

        # =====================================================
        # 6. RETURN
        # =====================================================

        return blocks

    # =========================================================
    # Combined bbox
    # =========================================================

    @staticmethod
    def _calculate_combined_bbox(
        records: List[OCRRecord],
    ) -> Tuple[
        float,
        float,
        float,
        float,
    ]:

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

    # =========================================================
    # Multiple pages
    # =========================================================

    def reconstruct_document(
        self,
        document,
    ) -> Dict[
        int,
        List[ContentBlock],
    ]:

        result = {}

        for page in document.pages:

            result[page.page] = (
                self.reconstruct_page(
                    page
                )
            )

        return result

