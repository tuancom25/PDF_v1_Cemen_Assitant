from dataclasses import dataclass, field
from typing import List, Optional

from ..ingestion.models import ContentBlock


@dataclass
class Group:
    group_id: int

    page: int

    content_blocks: List[ContentBlock] = field(
        default_factory=list
    )

    bbox: Optional[list] = None

    previous_group_id: Optional[int] = None
    next_group_id: Optional[int] = None

    metadata: dict = field(
        default_factory=dict
    )

    def add_block(self, block: ContentBlock):
        self.content_blocks.append(block)

    @property
    def text(self) -> str:
        return "\n".join(
            block.text
            for block in self.content_blocks
            if block.text
        )

    def calculate_bbox(self):
        if not self.content_blocks:
            return None

        xs1 = []
        ys1 = []
        xs2 = []
        ys2 = []

        for block in self.content_blocks:
            x1, y1, x2, y2 = block.bbox

            xs1.append(x1)
            ys1.append(y1)
            xs2.append(x2)
            ys2.append(y2)

        self.bbox = [
            min(xs1),
            min(ys1),
            max(xs2),
            max(ys2),
        ]

        return self.bbox