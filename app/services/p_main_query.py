
from app.services.embedding.embedding_service import EmbeddingService
from app.services.vector_store.faiss_store import FaissVectorStore

# embeddingService = EmbeddingService()
# faissVectorStore = FaissVectorStore(1024)
# #DIRECTORY_PATH =
# DIRECTORY_VER_5_SAVE= "data/vector_store/bge_m3/ver_5_x_page_x"
from app.services.embedding.embedding_service import ( EmbeddingService,)
from app.services.vector_store.faiss_store import ( FaissVectorStore,)


VECTOR_DIR = (
    "data/vector_store/bge_m3/ver_5_x_page_x"
)

# ----------------------------------------------------------
# LOAD EMBEDDING MODEL
# ----------------------------------------------------------
print()
print (" --- Start program ---")
print(" ---- Create model --- ")
embedder = EmbeddingService(
    model_name="BAAI/bge-m3",
    batch_size=4,
    normalize=True,
)
print("------- ")
print (" Complete load model ")
# ----------------------------------------------------------
# LOAD FAISS
# ----------------------------------------------------------
print()
print(" ---- Begin load data ")
store = FaissVectorStore(   dimension=embedder.dimension, )
store.load( VECTOR_DIR )
print(
    "Loaded vectors:",
    store.count,
)

while True :
   print ("#"*70)
   print (" ----- Xin mời đặt câu hỏi ----- \n")
   message = input()
   if message =="exit" or message == "Exit":
      break 
   question = message 
   query_vector = (
        embedder.encode_query(
          question
        )
    )
   results = store.search(
    query_vector,
    top_k=5,
    )
   for i, result in enumerate(
        results,
        start=1,
        ):

        print("=" * 70)

        print(
            f"Rank: {i}"
        )

        print(
            f"Score: {result['score']:.4f}"
        )

        print(
            "Chunk:",
            result["chunk_id"]
        )

        print(
            "Document:",
            result["document_id"]
        )

        print(
            "Page:",
            result["page_start"],
            "-",
            result["page_end"],
        )

        print(
            "Section:",
            result["section"]
        )
        print ( "text: ",result["text"] )