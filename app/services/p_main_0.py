#
# Viết chương trình  chính - luồng chương trình chính có 2 vòng While ( TRue) : ở đây 
# KHi test sẽ chạy vào chương trình chính - nhưng từng khúc của chương trình chính 
# cần load checkpoint , kiểm tra checkpoint trước 
# sau đó load list name document ,  println  list name đã xử lý
# tiếp tục xử lý từ điểm  xác nhận  checkpoint , 

## Mặc dù chưa hoàn thành nhưng TƯơng đối hiểu các phần chi tiết, 
# Và đây là luồng chính cần flow theo chương trình chính .  
def run_pipeline():
    loadCheckPoint() 

    documents = load_documents()

    for document in documents:

        for page in document.pages:

            # 1. Load / reconstruct
            content_blocks = ingestion.process(page)
            # 2. 
            group_result = group_service.process(content_blocks)
            # 3.
            groups = group_result.groups
            unassigned_groups = group_result.unassigned_groups

            # 4. Semantic analysis
            semantic_blocks = semantic_service.process(
                groups,
                unassigned_groups
            )

            # 5. Semantic grouping
            semantic_groups = semantic_group_service.process(
                semantic_blocks
            )
            # Khả năng ở đây là ok, vì công đoạn này không cần biết các công đoạn trước xa nó
            # nó không cần biết page, không cần biết contentblock nữa . nó đã chỉ cần semanticGroup rồi .  
            # 6. Chunking
            chunks = chunk_service.process(
                semantic_groups
            )

            # 7. Embedding
            vectors = embedding_service.process(
                chunks
            )

            # 8. Persist
            vector_store.save(
                vectors
            )