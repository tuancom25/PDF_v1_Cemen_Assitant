from typing import List
'''


from .models import BlockRole
from .semantic_content_block import (
    SemanticContentBlock,
)
from .semantic_group import SemanticGroup
'''
from app.services.ingestion.models import  (
    BlockRole,
    ContentBlock,
    SemanticContentBlock,
    BlockType,
    SemanticGroup,
    
    )

class SemanticGroupBuilder:

    def build(
        self,
        blocks: List[SemanticContentBlock],
    ) -> List[SemanticGroup]:

        if not blocks:
            return []

        blocks = sorted(
            blocks,
            key=lambda b: (
                b.page,
                b.bbox[1],
                b.bbox[0],
            ),
        )

        groups = []

        current = None

        for block in blocks:

            is_heading = (
                block.role
                == BlockRole.SECTION_HEADING
            )

            # -------------------------------------------------
            # First block
            # -------------------------------------------------

            if current is None:

                current = SemanticGroup(
                    semantic_group_id=len(groups),

                    page_start=block.page,

                    page_end=block.page,
                )

                current.blocks.append(block)

                continue

            # -------------------------------------------------
            # New semantic section
            # -------------------------------------------------

            if is_heading:

                current.page_end = (
                    current.blocks[-1].page
                )

                groups.append(current)

                current = SemanticGroup(
                    semantic_group_id=len(groups),

                    page_start=block.page,

                    page_end=block.page,
                )

                current.blocks.append(block)

                continue

            # -------------------------------------------------
            # Same semantic group
            # -------------------------------------------------

            current.blocks.append(block)

            current.page_end = block.page

        # -----------------------------------------------------
        # Flush
        # -----------------------------------------------------

        if current is not None:

            groups.append(current)

        # -----------------------------------------------------
        # Previous / next
        # -----------------------------------------------------

        for i, group in enumerate(groups):

            if i > 0:
                group.previous_id = (
                    groups[i - 1]
                    .semantic_group_id
                )

            if i < len(groups) - 1:
                group.next_id = (
                    groups[i + 1]
                    .semantic_group_id
                )

        return groups