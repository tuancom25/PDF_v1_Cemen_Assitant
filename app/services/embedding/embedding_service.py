from typing import List, Optional

from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(
        self,
        model_name: str,
        batch_size: int = 8,
        normalize: bool = True,
        device: Optional[str] = None,
    ):
        self.model_name = model_name
        self.batch_size = batch_size
        self.normalize = normalize

        if device is None:
            device = "cuda"

        self.device = device

        self.model = SentenceTransformer(
            model_name,
           # device=device,
        )

        self.dimension = (
            self.model.get_sentence_embedding_dimension()
        )

    # ----------------------------------------------------------
    # DOCUMENT / CHUNK
    # ----------------------------------------------------------

    def encode_documents(
        self,
        texts: List[str],
    ) -> List[List[float]]:

        texts = self._prepare_documents(texts)

        vectors = self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=self.normalize,
            show_progress_bar=True,
            convert_to_numpy=True,
        )

        return vectors.tolist()

    # ----------------------------------------------------------
    # QUERY
    # ----------------------------------------------------------

    def encode_query(
        self,
        text: str,
    ) -> List[float]:

        return self.encode_queries([text])[0]

    def encode_queries(
        self,
        texts: List[str],
    ) -> List[List[float]]:

        texts = self._prepare_queries(texts)

        vectors = self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=self.normalize,
            show_progress_bar=False,
            convert_to_numpy=True,
        )

        return vectors.tolist()

    # ----------------------------------------------------------
    # PREPARE DOCUMENT
    # ----------------------------------------------------------

    def _prepare_documents(
        self,
        texts: List[str],
    ) -> List[str]:

        # E5 cần "passage:"
        if "e5" in self.model_name.lower():

            return [
                f"passage: {text}"
                for text in texts
            ]

        # BGE-M3 dùng text gốc
        return texts

    # ----------------------------------------------------------
    # PREPARE QUERY
    # ----------------------------------------------------------

    def _prepare_queries(
        self,
        texts: List[str],
    ) -> List[str]:

        # E5 cần "query:"
        if "e5" in self.model_name.lower():

            return [
                f"query: {text}"
                for text in texts
            ]

        # BGE-M3 dùng text gốc
        return texts

    # ----------------------------------------------------------
    # CHUNKS
    # ----------------------------------------------------------

    def embed_chunks(
        self,
        chunks,
    ):

        texts = [
            chunk.text
            for chunk in chunks
        ]

        vectors = self.encode_documents(texts)

        results = []

        for chunk, vector in zip(chunks, vectors):

            results.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "vector": vector,
                    "dimension": len(vector),
                    "embedding_model": self.model_name,
                }
            )

        return results