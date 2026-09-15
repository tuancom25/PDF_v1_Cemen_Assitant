

'''
                 Candidate 1
                 BGE-M3
English → English
Vietnamese → English

                 Candidate 2
            multilingual-e5-large

English → English
Vietnamese → English

Candidate 3
smaller multilingual model
 '''

import time
from app.services.embedding.embedding_service import EmbeddingService

time_start = time.perf_counter()
time_current : float
print (" --- Start program ---")

print (" ---- Begin create model ")
embedder = EmbeddingService(
    #model_name="sentence-transformers/all-MiniLM-L6-v2",     # model có khoảng 2-3-4-500MB 
    #batch_size=32,
    #model_name="intfloat/multilingual-e5-large",
    #batch_size=4,
    model_name="BAAI/bge-m3",  # model này có 2.27Gb 
    batch_size=4,
)
print (" Complete create model ")
print("Model:", embedder.model_name)
print("Dimension:", embedder.dimension)
time_current = time.perf_counter()
t = time_current - time_start 
print (" thơi gian load model :  " + str (t) )

texts = [
    "The burning zone temperature affects clinker formation.",
    "Coating formation depends on liquid phase content.",
    "The raw meal enters the preheater.",
    "Xin chào, hello tình yêu của tôi , em đang ở đâu "
    "Mùa xuân sang có hoa anh đào",
    "Mùa xuân sang có hoa đào anh", 
    "Kiều càng sắc sảo mặn mà",
    "So bề tài sắc lại là phần hơn"
]

#vectors = embedder.embed_batch(texts)
vectors = embedder.encode_documents(texts)
print("Number of vectors:", len(vectors))
print("Vector dimension:", len(vectors[0]))
print("Vector dimension:", len(vectors[1]))
time_current= time.perf_counter()
tt = time_current - time_start

print(" thoi gian hoàn thành: " + str (tt/60) + ":" + str(tt%60))