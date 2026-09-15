
'''
@dataclass
class SemanticContentBlock:

    block_id: str

    text: str

    bbox: list

    page: int

    content_type: str

    role: BlockRole = BlockRole.UNKNOWN

    group_id: Optional[int] = None

    previous_block_id: Optional[str] = None

    next_block_id: Optional[str] = None

    source_block: Optional[ContentBlock] = None

    metadata: dict = field(
        default_factory=dict
    )

@define
class SemanticGroup:

    semantic_group_id: int

    blocks: List[
        SemanticContentBlock
    ] = field(factory=list)

    page_start: int = 0

    page_end: int = 0

    parent_id: Optional[int] = None

    previous_id: Optional[int] = None

    next_id: Optional[int] = None

    level: Optional[int] = None

    metadata: Dict[str, Any] = field(
        factory=dict
    )
    @property
    def text(self) -> str:

        return "\n".join(
            block.text
            for block in self.blocks
            if block.text
        )

    @property
    def heading(self) -> Optional[str]:

        for block in self.blocks:

            if block.role.value == (
                "section_heading"
            ):
                return block.text

        return None
'''