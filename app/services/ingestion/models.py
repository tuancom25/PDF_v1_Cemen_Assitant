from attrs import define, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

@define
class OCRRecord:
    text: str

    # Polygon gốc từ PaddleOCR:
    # [
    #   [x1, y1],
    #   [x2, y2],
    #   [x3, y3],
    #   [x4, y4]
    # ]
    polygon: List[List[float]]

    confidence: Optional[float] = None

    @property
    def bbox(self) -> Tuple[float, float, float, float]:
        """Chuyển polygon OCR thành bbox [x1, y1, x2, y2]."""
        xs = [point[0] for point in self.polygon]
        ys = [point[1] for point in self.polygon]

        return (
            min(xs),
            min(ys),
            max(xs),
            max(ys),
        )

    @property
    def center(self) -> Tuple[float, float]:
        """Tâm của bbox OCR."""
        x1, y1, x2, y2 = self.bbox

        return (
            (x1 + x2) / 2.0,
            (y1 + y2) / 2.0,
        )


@define
class LayoutBlock:
    index: int
    type: str
    score: Optional[float] = None

    # [x1, y1, x2, y2]
    bbox: Tuple[float, float, float, float] = field(
        factory=lambda: (0.0, 0.0, 0.0, 0.0)
    )


@define
class ContentBlock:
    """
    Kết quả reconstruct từ OCR + Layout.

    Đây là lớp trung gian trước Chunking.
    """
     
    block_id: str
    

    content_type: str

    page: int

    text: str = ""
    
    
    bbox: Tuple[float, float, float, float] = field(
        factory=lambda: (0.0, 0.0, 0.0, 0.0)
    )

    confidence: Optional[float] = None

    layout_index: Optional[int] = None

    layout_score: Optional[float] = None
    # reading_order: int = 0

    ocr_records: List[OCRRecord] = field( factory=list )

    metadata: Dict[str, Any] = field(
        factory=dict
    )

    reading_order: Optional[int] = None
    block_index: int = -1

@define
class Page:
    document_id: str

    source_file: str

    page: int

    width: float

    height: float

    page_type: str

    text_chars: int = 0

    image_count: int = 0

    drawing_count: int = 0

    native_text: Optional[str] = None

    text_blocks: List[Any] = field(
        factory=list
    )

    ocr_records: List[OCRRecord] = field(
        factory=list
    )

    layout_blocks: List[LayoutBlock] = field(
        factory=list
    )

    images: List[Dict[str, Any]] = field(
        factory=list
    )

    vector: Optional[Dict[str, Any]] = None

    ocr_file: Optional[str] = None

    ocr_record_count: int = 0

    warnings: List[str] = field(
        factory=list
    )


@define
class Document:
    document_id: str

    source_file: str

    metadata: Dict[str, Any] = field(
        factory=dict
    )

    pages: List[Page] = field(
        factory=list
    )
#@define
class BlockType(str, Enum):
    TEXT = "text"
    TABLE = "table"
    FIGURE = "figure"
    UNKNOWN = "unknown"
'''
@define
class BlockRole(str, Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    CAPTION = "caption"
    TABLE = "table"
    FIGURE = "figure"
    UNKNOWN = "unknown"
'''



#@define
class BlockRole_(str, Enum):
    UNKNOWN = "unknown"
    SECTION_HEADING = "section_heading"
    PARAGRAPH = "paragraph"
    DEFINITION = "definition"
    EXPLANATION = "explanation"
    FIGURE_CAPTION = "figure_caption"
    TABLE_CAPTION = "table_caption"
    TECHNICAL_TABLE = "technical_table"
    EQUATION = "equation"
    LIST = "list"
    FOOTNOTE = "footnote"
    
# Nếu không xác định được role,
#  thì mặc định có thể là PARAGRAPH
class BlockRole(str, Enum):

    UNKNOWN = "unknown"
    # Structure
    DOCUMENT_TITLE = "document_title"
    SECTION_HEADING = "section_heading"
    PARAGRAPH = "paragraph"
# nếu không xac định được role, thì mặc định là PARAGRAPH
    # Technical semantic
    DEFINITION = "definition"
    EXPLANATION = "explanation"

    # Figures / tables
    FIGURE = "figure"
    FIGURE_CAPTION = "figure_caption"
    TECHNICAL_TABLE = "technical_table"
    TABLE_CAPTION = "table_caption"

    # Mathematical / structured content
    EQUATION = "equation"
    LIST = "list"

    # Supporting content
    FOOTNOTE = "footnote"
'''
SECTION_HEADING
PARAGRAPH
DEFINITION
EXPLANATION
FIGURE_CAPTION
TABLE_CAPTION
TECHNICAL_TABLE
EQUATION
LIST
FOOTNOTE
'''
#FIGURE_CAPTION
#FIGURE
#TABLE_CAPTION
#TECHNICAL_TABLE
#SECTION_HEADING
#PARAGRAPH
#EQUATION

#@dataclass
@define
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
        factory=dict
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

# Phân vân : trong chunk có document_name để truy suất document 
# có document_page để truy suất document_page_number cho nó nhanh
@define
class Chunk:

    chunk_id: str
    document_id: str
    chunk_index: int

    text: str

    page_start: int
    page_end: int

    section: Optional[str] = None
    subsection: Optional[str] = None
    heading: Optional[str] = None

    block_indices: List[int] = field(factory=list)

    prev_chunk_id: Optional[str] = None
    next_chunk_id: Optional[str] = None

    metadata: Optional["ChunkMetadata"] = None


@define
class ChunkMetadata:

    language: str = "en"

    roles: List[str] = field(factory=list)

    source_blocks: List[dict] = field(factory=list)

    text_length: int = 0

    embedding_model: Optional[str] = None
    embedding_dimension: Optional[int] = None


#========================================================================
#     
'''

@define
class ChunkMetadata:

    # Identity
    chunk_id: str
    document_id: str
    chunk_index : int 

    # Language
    language: str = "en"

    # Document location
    page_start: int = 0
    page_end: int = 0

    # Semantic location
    section: Optional[str] = None
    subsection: Optional[str] = None
    heading: Optional[str] = None

    # Content characteristics
    #roles: List[str] = field(default_factory=list)
    roles: List[str] = field(factory=list)

    # Traceability
    #source_blocks: List[dict] = field(default_factory=list)
    source_blocks: List[dict] = field(factory=list)
    block_indices: List[int] = field(factory=list)
    # Retrieval
    text_length: int = 0
    prev_chunk_id : str 
    next_chunk_id : str

    # Embedding
    embedding_model: Optional[str] = None
    embedding_dimension: Optional[int] = None

@define
class Chunk:
    chunk_id: str
    document_id: str
    text: str
    page_start: int
    page_end: int
    section: Optional[str] = None
    subsection: Optional[str] = None
    #block_indices: List[int] = field(default_factory=list)
    block_indices: List[int] = field(factory=list)
    metadata: Optional[ChunkMetadata] = None

    chunk_index : int
    prev_chunk_id: Optional[str] = None
    next_chunk_id: Optional[str] = None
'''
'''
@define
class EmbeddedChunk:

    chunk_id: str

    vector: list

    embedding_model: str

    dimension: int
'''
'''    
@define
class Chunk:
    chunk_id: str
    document_id: str
    text: str
    page_start: int
    page_end: int
    section: Optional[str] = None
    subsection: Optional[str] = None
    block_indices: List[int] = field(factory=list)
'''
