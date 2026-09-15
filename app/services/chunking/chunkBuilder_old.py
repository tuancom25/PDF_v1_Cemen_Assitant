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
        max_chars: int = 1800,
        min_chars: int = 300,
    ):
        self.max_chars = max_chars
        self.min_chars = min_chars

    # =====================================================
    # PUBLIC
    # =====================================================

    def build(
        self,
        semantic_groups: List[SemanticGroup],
        document_id: str,
    ) -> List[Chunk]:

        if not semantic_groups:
            return []

        chunks: List[Chunk] = []

        for group in semantic_groups:

            group_chunks = self._build_group_chunks(
                group=group,
                document_id=document_id,
                start_index=len(chunks),
            )

            chunks.extend(group_chunks)

        return chunks

    # =====================================================
    # BUILD ONE SEMANTIC GROUP
    # =====================================================

    def _build_group_chunks(
        self,
        group: SemanticGroup,
        document_id: str,
        start_index: int,
    ) -> List[Chunk]:

        chunks: List[Chunk] = []

        buffer: List[SemanticContentBlock] = []
        buffer_chars = 0

        chunk_index = start_index

        for block in group.blocks:

            text = self._block_text(block)

            if not text:
                continue

            block_chars = len(text)

            # =================================================
            # ATOMIC BLOCK
            #
            # Table / Equation / Figure
            # được giữ thành chunk riêng
            # =================================================

            if self._is_atomic_block(block):

                # ---------------------------------------------
                # Flush text buffer trước
                # ---------------------------------------------

                if buffer:

                    chunks.append(
                        self._flush(
                            blocks=buffer,
                            chunk_index=chunk_index,
                            document_id=document_id,
                        )
                    )

                    chunk_index += 1

                    buffer = []
                    buffer_chars = 0

                # ---------------------------------------------
                # Atomic block -> own chunk
                # ---------------------------------------------

                chunks.append(
                    self._flush(
                        blocks=[block],
                        chunk_index=chunk_index,
                        document_id=document_id,
                    )
                )

                chunk_index += 1

                continue

            # =================================================
            # MAX CHARS
            # =================================================

            if (
                buffer
                and
                buffer_chars + block_chars
                > self.max_chars
            ):

                chunks.append(
                    self._flush(
                        blocks=buffer,
                        chunk_index=chunk_index,
                        document_id=document_id,
                    )
                )

                chunk_index += 1

                buffer = []
                buffer_chars = 0

            # =================================================
            # ADD BLOCK
            # =================================================

            buffer.append(block)
            buffer_chars += block_chars

        # =====================================================
        # FLUSH REMAINING
        # =====================================================

        if buffer:

            chunks.append(
                self._flush(
                    blocks=buffer,
                    chunk_index=chunk_index,
                    document_id=document_id,
                )
            )

        return chunks

    # =====================================================
    # ATOMIC BLOCK
    # =====================================================

    def _is_atomic_block(
        self,
        block: SemanticContentBlock,
    ) -> bool:

        return block.role in {

            BlockRole.TECHNICAL_TABLE,

            BlockRole.EQUATION,

            BlockRole.FIGURE,
        }

    # =====================================================
    # GET BLOCK TEXT
    # =====================================================

    def _block_text(
        self,
        block: SemanticContentBlock,
    ) -> str:

        if not block.text:
            return ""

        return block.text.strip()

    # =====================================================
    # FLUSH
    # =====================================================

    def _flush(
        self,
        blocks: List[SemanticContentBlock],
        chunk_index: int,
        document_id: str,
    ) -> Chunk:

        text_parts = []

        pages = []

        block_indices = []

        section: Optional[str] = None
        subsection: Optional[str] = None

        # =================================================
        # Collect block information
        # =================================================

        for block in blocks:

            # ---------------------------------------------
            # Text
            # ---------------------------------------------

            if block.text:

                text_parts.append(
                    block.text.strip()
                )

            # ---------------------------------------------
            # Page
            # ---------------------------------------------

            pages.append(block.page)

            # ---------------------------------------------
            # Block index
            # ---------------------------------------------

            if hasattr(block, "block_index"):

                block_indices.append(
                    block.block_index
                )

            elif hasattr(block, "index"):

                block_indices.append(
                    block.index
                )

            # ---------------------------------------------
            # Section
            # ---------------------------------------------

            if (
                block.role
                == BlockRole.SECTION_HEADING
            ):

                if section is None:

                    section = block.text

                else:

                    subsection = block.text

        # =================================================
        # Safety
        # =================================================

        if not pages:
            return None

        # =================================================
        # Remove duplicated pages
        # =================================================

        pages = sorted(
            set(pages)
        )

        # =================================================
        # Create chunk ID
        # =================================================

        chunk_id = (
            f"{document_id}_chunk_{chunk_index:06d}"
        )

        # =================================================
        # Create Chunk
        # =================================================

        return Chunk(

            chunk_id=chunk_id,

            document_id=document_id,

            text="\n\n".join(
                text_parts
            ),

            page_start=min(pages),

            page_end=max(pages),

            section=section,

            subsection=subsection,

            block_indices=block_indices,
        )