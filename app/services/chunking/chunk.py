from dataclasses import dataclass, field
from typing import Optional, List

from attr import define

# chú ý class Chunk này có vẻ  trùng với class Chunk trong models.py, 
@define
class Chunk:
    chunk_id: str
    document_id: str

    text: str

    page_start: int
    page_end: int

    section: Optional[str] = None
    subsection: Optional[str] = None

    block_indices: List[int] = field(default_factory=list)
'''
class Chunker :
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size

    def chunk_text(self, text: str) -> List[str]:
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunks.append(text[i:i + self.chunk_size])
        return chunks
'''
 