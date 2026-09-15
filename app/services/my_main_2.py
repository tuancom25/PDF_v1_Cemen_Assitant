"""
app/
│
├── ingestion/
│   ├── loader.py
│   ├── reconstructor.py
│   └── models.py
│
├── group/
│   ├── __init__.py
│   └── unassigned_group.py
│
├── semantic/
│   ├── __init__.py
│   ├── semantic.py
│   ├── context.py
│   └── semantic_group.py
│
├── chunking/
│   ├── __init__.py
│   ├── chunk.py
│   └── chunker.py
│
├── embedding/
│   ├── __init__.py
│   ├── embedder.py
│   └── buffer.py
│
├── storage/
│   ├── __init__.py
│   ├── chunk_store.py
│   └── vector_store.py
│
└── pipeline/
    ├── __init__.py
    └── document_pipeline.py
"""
"""
while còn PDF:
│
├── load PDF
│
└── while còn Page:
    │
    ├── load Page
    │
    ├── reconstruct
    │       ↓
    │   ContentBlock[]
    │
    └── while còn ContentBlock:
            │
            ├── GROUP
            │
            ├── đủ điều kiện
            │       ↓
            │   SEMANTIC
            │
            ├── đủ điều kiện
            │       ↓
            │    CHUNK
            │
            └── đủ batch
                    ↓
                EMBEDDING
"""
semantic_processor = SemanticProcessor()
semantic_group_builder = SemanticGroupBuilder()
chunker = Chunker()
embedding_buffer = EmbeddingBuffer()

#====== -------------------------
while pdf_remaining:

    open_document()

    while page_remaining:

        page = read_page()

        blocks = reconstruct(page)

        for block in blocks:

            ...
## Mã giả đầy đủ : 
while pdf_reader.has_next():

    document = pdf_reader.next()

    semantic_processor.reset()
    semantic_group_builder.reset()

    while document.has_next_page():

        page = document.next_page()

        blocks = reconstruct(page)

        for block in blocks:

            completed_group = grouper.push(block)

            if completed_group:

                semantic_blocks = semantic_processor.process(
                    completed_group
                )

                for semantic_block in semantic_blocks:

                    completed_semantic_group = (
                        semantic_group_builder.push(
                            semantic_block
                        )
                    )

                    if completed_semantic_group:

                        chunks = chunker.process(
                            completed_semantic_group
                        )

                        embedding_buffer.add_many(
                            chunks
                        )

                        if embedding_buffer.is_ready():

                            vectors = embedder.embed(
                                embedding_buffer.flush()
                            )

                            storage.save_embeddings(
                                vectors
                            )

#---------------
''' Cuối document phải có:'''
grouper.flush()
semantic_processor.flush()
semantic_group_builder.flush()
chunker.flush()
embedding_buffer.flush()