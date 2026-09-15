from typing import List, Optional

'''from app.models import (
    ContentBlock,
    SemanticContentBlock,
    BlockRole,
    BlockType,

)'''
from app.services.group.unassigned_group_old_2 import UnassignedGroup
from app.services.ingestion.models import  ( 
    BlockRole,  
    ContentBlock,
    SemanticContentBlock,
    BlockType,
    SemanticGroup,
    
    )
from semantic_context import SemanticContext 

class SemanticProcessor:

    def __init__(self):
        self.context = SemanticContext()

    def reset(self):
        self.context = SemanticContext()

    def process(
        self,
        group: UnassignedGroup
    ) -> list[SemanticContentBlock]:

        ...


class SemanticGroupBuilder:

    def __init__(self):
        self._current_blocks = []

    def reset(self):
        self._current_blocks = []

    def push(
        self,
        block: SemanticContentBlock
    ) -> Optional[SemanticGroup]:

        ...

    def flush(self) -> Optional[SemanticGroup]:

        ...

def detect_role(block: ContentBlock) -> BlockRole:

    if block.content_type == "table":
      return BlockRole.TABLE

    if block.content_type == "figure":
       return BlockRole.FIGURE
    ''' 
    if block.type == BlockType.TABLE:
        return BlockRole.TABLE

    if block.type == BlockType.FIGURE:
        return BlockRole.FIGURE
    '''
    text = block.text.strip()

    if not text:
        return BlockRole.UNKNOWN

    if _is_caption(text):
        return BlockRole.CAPTION

    if _is_heading(block):
        return BlockRole.HEADING

    return BlockRole.PARAGRAPH


def _is_caption(text: str) -> bool:

    text_lower = text.lower()

    prefixes = (
        "figure ",
        "fig. ",
        "fig ",
        "table ",
    )

    return text_lower.startswith(prefixes)


def _is_heading(block: ContentBlock) -> bool:

    text = block.text.strip()

    if len(text) > 150:
        return False

    if _looks_like_numbered_heading(text):
        return True

    if _looks_like_short_heading(text):
        return True

    return False


def _looks_like_numbered_heading(text: str) -> bool:

    import re

    pattern = r"^\d+(\.\d+)*\.?\s+\S+"

    return bool(re.match(pattern, text))


def _looks_like_short_heading(text: str) -> bool:

    words = text.split()

    if len(words) > 12:
        return False

    if text.endswith("."):
        return False

    return True

def to_semantic_block(
    block: ContentBlock,
    role: BlockRole,
    group_id: int,
) -> SemanticContentBlock:

    return SemanticContentBlock(
        block_id=block.block_id,
        content_type=block.content_type,
        page=block.page,
        text=block.text,
        bbox=block.bbox,
        confidence=block.confidence,
        layout_index=block.layout_index,
        layout_score=block.layout_score,
        reading_order=block.reading_order,
        ocr_records=block.ocr_records,
        metadata=block.metadata.copy(),
        role=role,
        group_id=group_id,
    )


def process_group(
    group_id: int,
    block_indices: List[int],
    blocks: List[ContentBlock],
) -> SemanticGroup:

    semantic_blocks = []

    for index in block_indices:
        block = blocks[index]

        role = detect_role(block)

        semantic_block = to_semantic_block(
            block=block,
            role=role,
            group_id=group_id,
        )

        semantic_blocks.append(semantic_block)

    return SemanticGroup(
        group_id=group_id,
        blocks=semantic_blocks,
    )


def process_groups(
    groups: List[List[int]],
    blocks: List[ContentBlock],
) -> List[SemanticGroup]:

    result = []

    for group_id, block_indices in enumerate(groups):

        semantic_group = process_group(
            group_id=group_id,
            block_indices=block_indices,
            blocks=blocks,
        )

        result.append(semantic_group)

    return result