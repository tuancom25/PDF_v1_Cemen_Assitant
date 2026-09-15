# ============================================================
# this is ver 5.1
# this file name to run  :: python -m app.services.p_main_5_1 
# p_main_5_1.py
# từ version 5.0 này  đã sửa việc thừa 1 vòng lặp for document in list_of_documents:  , vì đã có vòng for document_index, pdf in enumerate(pdf_files):  rồi.
# phiên bản này đang chunking qua nhiều page
#( còn  môt phiên bản 4.x - chunking theo page  . )
# Bản này là ver 5.1 là bản làm sạch comment test của ver 5
# MAIN PIPELINE
#
# PDF
#   ↓
# Document
#   ↓
# Page
#   ↓
# ContentBlock
#   ↓
# Group
#   ↓
# UnassignedGroup
#   ↓
# SemanticContentBlock
#   ↓
# SemanticGroup
#   ↓
# Chunk
#
# OCR / LayoutParser / Reconstruct
# đã được thực hiện trước đó.
#
# Main chỉ đọc dữ liệu đã xử lý và chạy các tầng tiếp theo.
# ============================================================
import time

from pathlib import Path
from typing import List
import os

# ============================================================
# 1. IMPORT MODELS
# ============================================================

from app.services.ingestion.models import (
    ContentBlock,
    SemanticContentBlock,
)


# ============================================================
# 2. IMPORT LOADERS
# ============================================================
from app.services.ingestion.loader import ( DocumentLoader )




# ============================================================
# 3. IMPORT RECONSTRUCTOR
# ============================================================

from app.services.ingestion.reconstruct import (  DocumentReconstructor, )



# ============================================================
# 4. IMPORT GROUP
# ============================================================

from app.services.group.group_builder import (
    GroupBuilder,
)
# Chưa có import UnassignedGroupBuilder vì chưa viết xong, nhưng đã có class UnassignedGroup
# Mới sửa lại import UnassignedGroupBuilder từ unassigned_group.py
from app.services.group.unassigned_group import (     UnassignedGroupBuilder,)


# ============================================================
# 5. IMPORT SEMANTIC
# ============================================================

from app.services.semantic.semantic_builder import (
    SemanticBuilder,
)

from app.services.semantic.semantic_group_builder import (
    SemanticGroupBuilder,
)


# ============================================================
# 6. IMPORT CHUNKING
# ============================================================
#from app.services.chunking.chunk import ( Chunk  )
from app.services.chunking.chunkBuilder import ( ChunkBuilder,  )
#from app.services.chunking.chunker import (  Chunker, )


# ============================================================
# 7. IMPORT CHECKPOINT
# ============================================================

from app.services.checkpoint.checkpoint_manager import (
    CheckpointManager,
)

from app.services.embedding.embedding_service import ( EmbeddingService )

from app.services.vector_store.faiss_store import (
     FaissVectorStore
)

# ============================================================
# 8. CONFIGURATION
# ============================================================

DOCUMENT_ROOT = Path(
    "data/processed/documents"
)

CHECKPOINT_ROOT = Path(
    "data/checkpoints"
)
DIRECTORY_VER_5_SAVE= "data/vector_store/bge_m3/ver_5_x_page_x"
DIRECTORY_VER_4_SAVE= "data/vector_store/bge_m3/ver_4_x_page_1"


# ============================================================
# 9. CREATE SERVICES
# ============================================================

document_loader = DocumentLoader()

reconstructor = DocumentReconstructor()

group_builder = GroupBuilder()

unassigned_builder = UnassignedGroupBuilder()

semantic_builder = SemanticBuilder()

semantic_group_builder = SemanticGroupBuilder()
embedder = EmbeddingService(
                #model_name="sentence-transformers/all-MiniLM-L6-v2",     # model có khoảng 2-3-4-500MB 
                #batch_size=32,
                #model_name="intfloat/multilingual-e5-large",
                #batch_size=4,
                model_name="BAAI/bge-m3",  # model này có 2.27Gb 
                batch_size=4,
            )
faissVectorStore = FaissVectorStore(embedder.dimension)  

#chunker = Chunker()
#chunker_builder = ChunkBuilder()
checkpoint_manager = CheckpointManager(
    CHECKPOINT_ROOT
)



# ============================================================
# 10. READ PDF DOCUMENT LIST
# ============================================================

def get_pdf_list(root: Path) -> List[Path]:

    """
    Lấy danh sách PDF cần xử lý.

    Lưu ý:
    - Không OCR ở đây.
    - Không LayoutParser ở đây.
    - Chỉ lấy danh sách document.
    documents = []
    documents = document_path.glob("*")
    """

    pdf_files = sorted(
       # root.rglob("*.pdf")
        root.glob("*")
    )

    return pdf_files


# ============================================================
# 11. MAIN
# ============================================================

def main():
    start_time = time.perf_counter()
    curent_time = time.perf_counter()
    print("=" * 70)
    print("PDF SEMANTIC PIPELINE")
    print("=" * 70)

    # --------------------------------------------------------
    # STEP 1
    # Đọc danh sách PDF
    # --------------------------------------------------------

    pdf_files = get_pdf_list(
        DOCUMENT_ROOT
    )

    total_documents = len(
        pdf_files
    )

    print(
        f"Total documents : {total_documents}"
    )

    print()

    document_path = "data/processed/documents"
    # pdf_files : là list tên các file pdf , hoặc  tên các thư mục, nằm trong app/data/processed/documents 
    for document in  pdf_files: 
            
            dir = document_path + "/"+  document.stem + "/pages"
            print ( dir)
    # --------------------------------------------------------
    # STEP 2
    # Duyệt document
    # --------------------------------------------------------
    curent_time = time.perf_counter()
    time_start_document =  time.perf_counter()
    vectors_all_prject =[]
    # số 378 là sô chiều của - của vector 
    # Số 378 phải lấy từ vector 
    curent_chunk_index = 0 
    for document_index, pdf in enumerate(
        pdf_files
    ):
            time_start_document =  time.perf_counter()
            document_name = pdf.stem

            print()
            print("=" * 70)

            print(
                f"DOCUMENT "
                f"{document_index + 1}/"
                f"{total_documents}"
            )

            print(
                f"Name : {document_name}"
            )

            print("=" * 70)


            # ====================================================
            # CHECKPOINT - DOCUMENT
            # Check
            # ====================================================
    
            document_checkpoint = (
                checkpoint_manager
                .load_document_checkpoint(
                    document_name
                )
            )


            # ----------------------------------------------------
            # Nếu document đã hoàn thành
            # ----------------------------------------------------

            if (
                document_checkpoint
                and
                document_checkpoint.get(
                    "status"
                ) == "complete"
            ):

                print(
                    "SKIP document "
                    "(already complete)"
                )

                continue


            # ====================================================
            # LOAD DOCUMENT
            # load chi tiết từ file json đã được OCR và LayoutParser xử lý trước đó.
            
            # ====================================================           
            print(
                    "Loading document..."
            )
        # ====================================================
        # DOCUMENT PAGE LOOP
        # ====================================================
            document = document_name
            print(" data in: " + document)
            page_json = document_path + "/"+  document + "/pages"
            #path_of_document_page = Path(document)
            path_of_document_page = Path(page_json)
            document_details = path_of_document_page.glob("*.json")
            
            total_pages = len(list(document_details))

            print(   f"Pages : {total_pages}"  )
            page_index = 0
            chunker_builder = ChunkBuilder(
                document_id=document_name,
                max_chars=1800,
                min_chars=300,
                curent_index= curent_chunk_index
            )
            for document_page_details in path_of_document_page.glob("*.json"):
                print (document_page_details)
                #from app.services.ingestion.loader import DocumentLoader
                project_root = Path.cwd()
                loader = DocumentLoader(
                        project_root=project_root
                    )
                
                print ("Path_Page:   " + document_page_details.stem)
                page = loader.load_page_json(document_page_details)
                page_number = page.page
                
                #print(
                #    f"Document : "
                #    f"{document_details.parent.parent.name}"
                #)
                print(
                    f"Page : "
                    f"{page_number}/"
                    f"{total_pages}"
                )

                page_index +=1
                page_number = (
                    page_index + 1
                )

                print()
                print(
                    "-" * 70
                )

                print(
                    f"Document : "
                    f"{document_name}"
                )

                print(
                    f"Page : "
                    f"{page_number}/"
                    f"{total_pages}"
                )

                print(
                    "-" * 70
                )

                # =================================================
                # 1. RECONSTRUCT
                # =================================================

                print(
                    "[1] RECONSTRUCT"
                )

                content_blocks = (
                    reconstructor
                    .reconstruct_page(
                        page
                    )
                )

                print(
                    f"    ContentBlocks : "
                    f"{len(content_blocks)}"
                )

                # =================================================
                # 2. GROUP
                # =================================================

                print(
                    "[2] GROUP"
                )

                groups =  group_builder.build( content_blocks)

                print(
                    f"    Groups : "
                    f"{len(groups)}"
                )

                # =================================================
                # 4. SEMANTIC CONTENT BLOCK
                # =================================================

                print(
                    "[4] SEMANTIC CONTENT BLOCK"
                )

                semantic_blocks = (
                    semantic_builder
                    .build(
                        groups
                    )
                )

                print(
                    f"    SemanticBlocks : "
                    f"{len(semantic_blocks)}"
                )


                # =================================================
                # 5. SEMANTIC GROUP
                # =================================================

                print(
                    "[5] SEMANTIC GROUP"
                )

                semantic_groups = (
                    semantic_group_builder
                    .build(
                        semantic_blocks
                    )
                )

                print(
                    f"    SemanticGroups : "
                    f"{len(semantic_groups)}"
                )


                # =================================================
                # 6. CHUNKING
                # =================================================
               
                print(
                    "[6] CHUNKING - chuẩn bị chunk" 
                )
                '''
                chunkers  = chunker_builder.build(
                    semantic_groups, 
                    document_id=document_name
                )
                print (
                    f"    Chunks : "
                    f"{len(chunkers)}"
                )
                 '''
                chunker_builder.add_groups(
                    semantic_groups
                )
                # =================================================
                # 7. SAVE / CHECKPOINT
                # =================================================
                '''
                print(
                    "[7] SAVE CHECKPOINT"
                )

                checkpoint_manager.mark_page_complete(
                    document_name,
                    page_number
                )
                '''

                # =================================================
                # PAGE FINISHED
                # =================================================

                print(
                    f"Page {page_number} "
                    f"completed."
                )


            # ====================================================
            # DOCUMENT FINISHED
            # ====================================================
            print()
            print(
                f"DOCUMENT COMPLETE : "
                f"{document_name}"
            )          
            chunks = chunker_builder.finalize()
            print()
            print(
                f"DOCUMENT CHUNKS : {len(chunks)}"
            ) 
            print ("-- Begin embedding --") 
            
 
            print("Model:", embedder.model_name)
            print("Dimension:", embedder.dimension)
        
            vectors =[]
            metadata=[] 
            #for chunk in chunks : 
            #     vector = embedder.embed_text(chunk.text) 
            #     vectors.append(vector)
            #     vectors_all_prject.append(vector)
            embedding_results = embedder.embed_chunks(chunks=chunks)
            #vectors = (r["vector"] for r in results )
            for item, chunk in zip(
                embedding_results,
                chunks,
            ):

                vectors.append(
                    item["vector"]
                )

                metadata.append(
                    {
                        "chunk_id": chunk.chunk_id,
                        "document_id": chunk.document_id,
                        "chunk_index": chunk.chunk_index,
                        "page_start": chunk.page_start,
                        "page_end": chunk.page_end,
                        "section": chunk.section,
                        "subsection": chunk.subsection,
                        "text" : chunk.text
                    }
                )
            curent_chunk_index += (len(vectors) -1 )     
            faissVectorStore.add(vectors, metadata)
            print ( "##  Save vector DB :.. ")
            print (" save path to: " + DIRECTORY_VER_5_SAVE)
            faissVectorStore.save(directory=DIRECTORY_VER_5_SAVE,model_name=embedder.model_name,normalize=True,)
            curent_time = time.perf_counter()
            time_leng_document =  curent_time - time_start_document 
            print ( "time: " + str(time_leng_document) + " s; doc: " + document_name +". ")
    # ========================================================
    # ALL DOCUMENTS FINISHED
    # ========================================================
    print ()
    print (" total Chunk =  " + str(curent_chunk_index))
    print()
    print("=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)
   
    time_total =0 
    curent_time = time.perf_counter()
    time_total = curent_time - start_time 
    print ("Total time :" + str(time_total//60) +":"+ str(time_total%60) + " s")
# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()