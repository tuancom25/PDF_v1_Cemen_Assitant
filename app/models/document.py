
from attrs import define, field

@define
class OCRRecord:
    text: str
    bbox: list[float]
    confidence: float | None = None


@define
class LayoutBlock:
    index: int
    type: str
    score: float | None
    bbox: list[float]


@define
class Page:
    page_number: int
    width: float
    height: float
    page_type: str

    native_text: str | None = None

    text_blocks: list = field(factory=list)
    ocr: list[OCRRecord] = field(factory=list)
    layout: list[LayoutBlock] = field(factory=list)

    images: list = field(factory=list)
    vector: dict | None = None


@define
class Document:
    document_id: str
    source_file: str
    metadata: dict
    pages: list[Page] = field(factory=list)