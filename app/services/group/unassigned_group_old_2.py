from dataclasses import dataclass
from typing import List

#from app.models.content_block import ContentBlock
from app.services.ingestion.models import (
    BlockType, 
    BlockRole, 
    ContentBlock,

)

@dataclass
class UnassignedGroup:
    group_id: int
    block_indices: List[int]


def group_blocks(
    blocks: List[ContentBlock],
) -> List[UnassignedGroup]:
    """
    Structural grouping.

    Group does NOT determine semantic role such as:
        heading
        paragraph
        caption

    It only groups ContentBlocks according to structural boundaries.
    """

    groups: List[UnassignedGroup] = []

    current_indices: List[int] = []

    def flush_current_group():
        nonlocal current_indices

        if not current_indices:
            return

        groups.append(
            UnassignedGroup(
                group_id=len(groups),
                block_indices=current_indices,
            )
        )

        current_indices = []

    for block in blocks:
        
        # Figure / table are structural objects.
        # Keep them isolated from normal text flow.
        if block.content_type in {"figure", "table"}:

            flush_current_group()

            groups.append(
                UnassignedGroup(
                    group_id=len(groups),
                    block_indices=[block.index],
                )
            )

            continue

        # Normal text-like content
        current_indices.append(block.index)

    flush_current_group()

    return groups