
'''
Sử dụng các ứng viên model . 
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


from typing import List
from sentence_transformers import SentenceTransformer

class EmbeddingService:

    def __init__(
        self,
        model_name: str,
        batch_size: int = 32,
        normalize: bool = True,
    ):

        self.model_name = model_name
        self.batch_size = batch_size
        self.normalize = normalize

        self.model = SentenceTransformer(model_name)

        self.dimension = self.model.get_sentence_embedding_dimension()

    def encode_documents(self, texts):
        ...

    def encode_queries(self, texts):
        ...
    
    def embed_text(self, text: str):

        vector = self.model.encode(
            text,
            normalize_embeddings=self.normalize,
        )
        return vector.tolist()

    def embed_batch(self, texts):

        vectors = self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=self.normalize,
            show_progress_bar=True,
        )
        return vectors.tolist()
    
    def embed_batch_2(
        self,
        texts: List[str],
    ) -> List[List[float]]:

        vectors = self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=self.normalize,
            show_progress_bar=True,
        )

        return vectors.tolist()

    @staticmethod 
    def embed_chunks(
        chunks,
        embedding_service,
        ):
        texts = [
            chunk.text
            for chunk in chunks
        ]
        vectors = embedding_service.embed_batch(texts)
        results = []
        for chunk, vector in zip(chunks, vectors):
            results.append({
                "chunk_id": chunk.chunk_id,
                "vector": vector,
                "dimension": len(vector),
                "embedding_model": embedding_service.model_name,
            })

        return results
