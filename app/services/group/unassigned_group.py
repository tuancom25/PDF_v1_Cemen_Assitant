#from dataclasses import dataclass, field
from typing import List, Optional
from attrs import define, field
from typing import List

#from  ..ingestion.models import ContentBlock
from app.services.ingestion.models import ContentBlock


class UnassignedGroup:

    group_id: int

    content_blocks: List[ContentBlock] = field(
        factory=list
    )

    reason: str = "unassigned"

    metadata: dict = field(
        factory=dict
    )

    @property
    def text(self) -> str:

        return "\n".join(
            block.text
            for block in self.content_blocks
            if block.text
        )
class UnassignedGroupBuilder:

    def __init__(self):
        self._current_blocks = []

    def reset(self):
        self._current_blocks = []

    def push(
        self,
        block: ContentBlock
    ) -> Optional[UnassignedGroup]:

        ...

    def flush(self) -> Optional[UnassignedGroup]:

        ...