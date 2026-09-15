from typing import List, Optional

from app.services.ingestion.models import (
    BlockRole,
    SemanticContentBlock,
    SemanticGroup,
    Chunk,
)


class ChunkBuilder:

    def __init__(
        self,
        document_id: str,
        max_chars: int = 1800,
        min_chars: int = 300,
        curent_index : int = 0
    ):
        self.document_id = document_id
        self.max_chars = max_chars
        self.min_chars = min_chars

        # =====================================================
        # DOCUMENT-LEVEL BUFFER
        # =====================================================

        self.buffer: List[SemanticContentBlock] = []
        self.buffer_chars = 0

        # =====================================================
        # CHUNK INDEX
        # =====================================================

        self.chunk_index = 0
        self.curent_index = curent_index
        # =====================================================
        # RESULT
        # =====================================================

        self.chunks: List[Chunk] = []

        # =====================================================
        # SECTION CONTEXT
        # =====================================================

        self.current_section: Optional[str] = None
        self.current_subsection: Optional[str] = None

    # =========================================================
    # PUBLIC
    # =========================================================

    def add_groups(
        self,
        semantic_groups: List[SemanticGroup],
    ) -> None:

        if not semantic_groups:
            return

        for group in semantic_groups:

            if not group.blocks:
                continue

            for block in group.blocks:

                self._add_block(block)

    # =========================================================
    # ADD ONE BLOCK
    # =========================================================

    def _add_block(
        self,
        block: SemanticContentBlock,
    ) -> None:

        text = self._block_text(block)

        if not text:
            return

        # -----------------------------------------------------
        # UPDATE SECTION CONTEXT
        # -----------------------------------------------------

        self._update_section_context(block)

        block_chars = len(text)

        # =====================================================
        # ATOMIC BLOCK
        # =====================================================

        if self._is_atomic_block(block):

            # Flush text đang có
            self._flush_buffer()

            # Atomic block = một chunk riêng
            self._emit_chunk(
                [block]
            )

            return

        # =====================================================
        # MAX CHARS
        # =====================================================

        if (
            self.buffer
            and
            self.buffer_chars + block_chars
            > self.max_chars
        ):

            self._flush_buffer()

        # =====================================================
        # ADD BLOCK
        # =====================================================

        self.buffer.append(block)
        self.buffer_chars += block_chars

    # =========================================================
    # FINALIZE DOCUMENT
    # =========================================================

    def finalize(self) -> List[Chunk]:

        self._flush_buffer()

        result = self.chunks

        # Không reset document_id.
        # Chỉ reset buffer để tránh giữ object không cần thiết.

        self.buffer = []
        self.buffer_chars = 0

        return result

    # =========================================================
    # FLUSH BUFFER
    # =========================================================

    def _flush_buffer(self) -> None:

        if not self.buffer:
            return

        # -----------------------------------------------------
        # MIN CHARS
        # -----------------------------------------------------

        # Hiện tại chưa ép merge chunk.
        # Chỉ dùng min_chars để tránh tạo chunk rỗng/quá nhỏ.
        #
        # Việc merge small chunk sẽ xử lý ở bước sau
        # khi semantic boundary được ổn định.

        self._emit_chunk(
            self.buffer
        )

        self.buffer = []
        self.buffer_chars = 0

    # =========================================================
    # EMIT CHUNK
    # =========================================================

    def _emit_chunk(
        self,
        blocks: List[SemanticContentBlock],
    ) -> None:

        chunk = self._flush(
            blocks=blocks,
            chunk_index=self.chunk_index,
            document_id=self.document_id,
        )

        if chunk is not None:

            self.chunks.append(chunk)

            self.chunk_index += 1

    # =========================================================
    # ATOMIC
    # =========================================================

    def _is_atomic_block(
        self,
        block: SemanticContentBlock,
    ) -> bool:

        return block.role in {

            BlockRole.TECHNICAL_TABLE,

            BlockRole.EQUATION,

            BlockRole.FIGURE,
        }

    # =========================================================
    # TEXT
    # =========================================================

    def _block_text(
        self,
        block: SemanticContentBlock,
    ) -> str:

        if not block.text:
            return ""

        return block.text.strip()

    # =========================================================
    # SECTION CONTEXT
    # =========================================================

    def _update_section_context(
        self,
        block: SemanticContentBlock,
    ) -> None:

        if block.role != BlockRole.SECTION_HEADING:
            return

        # -----------------------------------------------------
        # Heading đầu tiên
        # -----------------------------------------------------

        if self.current_section is None:

            self.current_section = block.text

            return

        # -----------------------------------------------------
        # Heading tiếp theo
        # -----------------------------------------------------

        self.current_subsection = block.text

    # =========================================================
    # FLUSH -> CHUNK
    # =========================================================

    def _flush(
        self,
        blocks: List[SemanticContentBlock],
        chunk_index: int,
        document_id: str,
    ) -> Optional[Chunk]:

        if not blocks:
            return None

        text_parts = []
        pages = []
        block_indices = []

        # =====================================================
        # COLLECT
        # =====================================================

        for block in blocks:

            if block.text:
                text_parts.append(
                    block.text.strip()
                )

            pages.append(
                block.page
            )

            if hasattr(block, "block_index"):

                block_indices.append(
                    block.block_index
                )

            elif hasattr(block, "index"):

                block_indices.append(
                    block.index
                )

        # =====================================================
        # SAFETY
        # =====================================================

        if not pages:
            return None

        pages = sorted(
            set(pages)
        )

        # =====================================================
        # CHUNK ID
        # =====================================================

        chunk_id = (
            f"{document_id}_chunk_{chunk_index:06d}"
        )

        # =====================================================
        # CREATE CHUNK
        # =====================================================

        return Chunk(

            chunk_id=chunk_id,
            chunk_index=chunk_index + self.curent_index,
            document_id=document_id,

            text="\n\n".join(
                text_parts
            ),

            page_start=min(pages),

            page_end=max(pages),

            section=self.current_section,

            subsection=self.current_subsection,

            block_indices=block_indices,
        )