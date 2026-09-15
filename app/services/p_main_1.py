#
# Viết chương trình  chính - luồng chương trình chính có 2 vòng While ( TRue) : ở đây 
# KHi test sẽ chạy vào chương trình chính - nhưng từng khúc của chương trình chính 
# Đây là phần để test luồng chương trình chính ở file  này  kết hợp để giảm thay đổi sửa trên 1 file 
# Chương trình chính về cơ bản không chứa logic thuật toán chi tiết 
# 
"""
 Một điều nữa: không để Pipeline biết chi tiết thuật toán

DocumentPipeline không nên biết:

Heading được phát hiện bằng cách nào?

Group boundary tính thế nào?

Semantic role xác định ra sao?

Chunk split theo bao nhiêu token?

Pipeline chỉ biết:

group = grouper.push(block)

semantic_blocks = semantic.process(group)

semantic_group = semantic_group_builder.push(block)

chunks = chunker.process(semantic_group)

vectors = embedder.embed(texts)

vector_store.add(...)
 """
# Ghép code vào chương trình chính . 

"""
Luồng chuong trình chính. 
sau khi suy nghĩ thì để luồng chính như sau ( 1 step thứ n không cần phải hiểu về step thứ n -2 , n-3 trước đó.)
 --
 đầu  tiên là load checkpoint  kiểm tra điểm hiện tại đang ở tài liệu nào , tên và thứ tự index . 
 load tất cả tên các document trong thư mục, vào list.
 lặp qua các document . 
  
 --- Bản chất vẫn duyệt qua các  page và block để xử lý , 
 --- Có lẽ đơn vị là block - 
 --- Nếu làm phẳng hoá thì mỗi lần xử lý có thể sẽ phải duyệt qua tất cảc page và block, 
 --- nhưng nếu làm theo luồng chính thì sẽ duyệt qua từng page và block,
 --- Nếu làm kiểu stream hì không cần load tất cả page và block vào bộ nhớ,
 ---  mà chỉ cần load từng page và block để xử lý.
"""
def run_pipeline():

    checkpoint = load_checkpoint()

    documents = load_documents()

    for document in documents:

        content_blocks = ingestion.process(document)

        group_result = group_service.process(
            content_blocks
        )

        semantic_blocks = semantic_service.process(
            group_result
        )

        semantic_groups = semantic_group_service.process(
            semantic_blocks
        )

        chunks = chunk_service.process(
            semantic_groups
        )

        vectors = embedding_service.process(
            chunks
        )

        vector_store.save(vectors)

        checkpoint.mark_complete(document)
