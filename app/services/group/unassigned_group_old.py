"""
Mục tiêu mới của unassigned_group.py

unassigned_group.py chỉ trả lời một câu hỏi:

Các ContentBlock nào thuộc cùng một nhóm structural?

Nó không trả lời:

block này là heading hay paragraph
block này là caption
block này thuộc section nào
hai block có cùng semantic topic hay không

Do đó:

ContentBlock[]
      │
      ▼
group_blocks()
      │
      ▼
UnassignedGroup[]
"""
from dataclasses import dataclass, field
from typing import List
from app.services.ingestion.models import (
    BlockType, 
    BlockRole, 
    ContentBlock,

)
# file này tên là : unassigned_group.py
@dataclass
class UnassignedGroup:
    group_id: int
    block_indices: List[int] = field(default_factory=list)
    current_type = None

def group_blocks(blocks):
    groups = []
    current = []

    for i, block in enumerate(blocks):

        role = block.get("role", "paragraph")

        # Heading bắt đầu group mới
        if role == "heading":

            if current:
                groups.append(current)

            current = [i]
            continue

        # Figure / table tạo group riêng
        if role in {"figure", "table"}:

            if current:
                groups.append(current)
                current = []

            current = [i]
            continue

        # Caption đi cùng figure/table
        if role == "caption":
            current.append(i)
            continue

        # Paragraph / text
        current.append(i)

    if current:
        groups.append(current)

    return groups

from dataclasses import dataclass, field
from typing import List, Callable

from app.models import ContentBlock, BlockRole


@dataclass
class UnassignedGroup:
    group_id: int
    block_indices: List[int] = field(default_factory=list)


def build_unassigned_groups(
    blocks: List[ContentBlock],
    role_detector: Callable[[ContentBlock], BlockRole],
) -> List[UnassignedGroup]:

    groups = []
    current = []

    for i, block in enumerate(blocks):

        role = role_detector(block)

        # Heading bắt đầu group mới
        if role == BlockRole.HEADING:
            if current:
                groups.append(current)

            current = [i]
            continue

        # Figure / table tạo group riêng
        if role in {BlockRole.FIGURE, BlockRole.TABLE}:
            if current:
                groups.append(current)
                current = []

            groups.append([i])
            continue

        # Caption đi cùng figure/table
        if role == BlockRole.CAPTION:
            current.append(i)
            continue

        # Paragraph / text
        current.append(i)

    if current:
        groups.append(current)

    return [
        UnassignedGroup(
            group_id=group_id,
            block_indices=indices,
        )
        for group_id, indices in enumerate(groups)
    ]

#def group_blocks_1(blocks): Tên hàm cũ chưa xoá . 
def build_unassigned_groups_old(blocks):
    groups = []
    current = []

    for i, block in enumerate(blocks):

        role = block.get("role", "paragraph")

        # Heading bắt đầu group mới
        if role == "heading":

            if current:
                groups.append(current)

            current = [i]
            continue

        # Figure / table tạo group riêng
        if role in {"figure", "table"}:

            if current:
                groups.append(current)
                current = []

            groups.append([i])
            continue

        # Paragraph / caption / text
        current.append(i)

    if current:
        groups.append(current)

    return [
        UnassignedGroup(
            group_id=i,
            block_indices=indices
        )
        for i, indices in enumerate(groups)
    ]


'''
def group_blocks_2(blocks):
        groups = []
        current = []

        for i, block in enumerate(blocks):

            role = block.get("role", "paragraph")

            if role == "heading":
                if current:
                    groups.append(current)

                current = [i]
                continue

            if role in {"figure", "table"}:
                if current:
                    groups.append(current)

                current = [i]
                continue

            if role == "caption":
                current.append(i)
                continue

            current.append(i)

        if current:
            groups.append(current)

        return groups
'''