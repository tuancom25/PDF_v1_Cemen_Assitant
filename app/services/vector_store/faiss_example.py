import faiss
import numpy as np 
import numpy as np
from sentence_transformers import SentenceTransformer 

dimension = 1024

index = faiss.IndexFlatIP(dimension)
