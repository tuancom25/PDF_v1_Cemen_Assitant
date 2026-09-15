"""
Chốt lại : 
- là phần ocr - layoutpaser  cần lưu data , đã lưu rồi 
- Phần lưu persitan tiếp là phần chunking và embedding vector DB .

"""
"""
 Kiến trúc sẽ dùng 2 vong flặp  while và vòng for để duyệt qua các pdf , page , contentbook 
 Đây là  phần main phần khung chức năng chương trình tùe read content -> embedding data vector DB

"""

for pdf in pdf_reader:

    document = load_document(pdf)

    for page in document.pages:

        # ============================================
        # 1. RECONSTRUCT
        # ============================================

        content_blocks = (
            reconstructor.reconstruct_page(
                page
            )
        )

        # ============================================
        # 2. GROUP
        # ============================================

        groups = group_builder.build(
            content_blocks
        )

        # ============================================
        # 3. UNASSIGNED
        # ============================================

        unassigned_groups = (
            unassigned_builder.build(
                content_blocks,
                groups
            )
        )

        # ============================================
        # 4. SEMANTIC CONTENT BLOCK
        # ============================================

        semantic_blocks = (
            semantic_builder.build(
                groups
            )
        )

        # ============================================
        # 5. SEMANTIC GROUP
        # ============================================

        semantic_groups = (
            semantic_group_builder.build(
                semantic_blocks
            )
        )

        # ============================================
        # 6. CHUNKING
        # ============================================

        chunks = chunker.build(
            semantic_groups
        )



