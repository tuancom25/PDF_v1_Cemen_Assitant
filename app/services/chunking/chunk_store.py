import json
from pathlib import Path

from app.services.chunking.chunk import Chunk


class ChunkStore:

    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    def save(self, chunks: list[Chunk]) -> None:

        with self.output_path.open(
            "a",
            encoding="utf-8"
        ) as f:

            for chunk in chunks:

                data = {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "text": chunk.text,
                    "page_start": chunk.page_start,
                    "page_end": chunk.page_end,
                    "section": chunk.section,
                    "subsection": chunk.subsection,
                    "block_indices": chunk.block_indices,
                }

                f.write(
                    json.dumps(
                        data,
                        ensure_ascii=False
                    )
                    + "\n"
                )