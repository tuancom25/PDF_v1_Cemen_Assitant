
# this is file: app/services/semantic/semantic_builder.py
from typing import List
from ..group.group import Group

from app.services.ingestion.models import  ( 
    BlockRole,  
    ContentBlock,
    SemanticContentBlock,
    BlockType,
    SemanticGroup,   
    )

from .role_detector import detect_role


class SemanticBuilder:

    def build(
        self,
        groups: List[Group],
    ) -> List[SemanticContentBlock]:

        result = []

        for group in groups:

            blocks = group.content_blocks

            for i, block in enumerate(blocks):

                role = detect_role(block)

                previous_id = None
                next_id = None

                if i > 0:
                    previous_id = (
                        blocks[i - 1].block_id
                    )

                if i < len(blocks) - 1:
                    next_id = (
                        blocks[i + 1].block_id
                    )

                semantic_block = (
                    SemanticContentBlock(
                        block_id=block.block_id,

                        text=block.text,

                        bbox=block.bbox,

                        page=block.page,

                        content_type=(
                            block.content_type
                        ),

                        role=role,

                        group_id=group.group_id,

                        previous_block_id=(
                            previous_id
                        ),

                        next_block_id=(
                            next_id
                        ),

                        source_block=block,

                        metadata={
                            "layout_index":
                                block.layout_index,

                            "layout_score":
                                block.layout_score,

                            "ocr_confidence":
                                block.confidence,
                        },
                    )
                )

                result.append(
                    semantic_block
                )

        return result