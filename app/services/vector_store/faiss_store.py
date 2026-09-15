import json
from pathlib import Path
from typing import List, Dict, Any

import faiss
import numpy as np


class FaissVectorStore:

    def __init__(
        self,
        dimension: int,
    ):

        self.dimension = dimension

        # Với normalized vectors:
        # Inner Product = Cosine Similarity
        self.index = faiss.IndexFlatIP(
            dimension
        )

        # metadata[i] tương ứng với
        # vector i trong FAISS
        self.metadata: List[Dict[str, Any]] = []

    # ==========================================================
    # ADD
    # ==========================================================

    def add(
        self,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
    ):

        if len(vectors) != len(metadata):
            raise ValueError(
                "vectors and metadata "
                "must have the same length"
            )

        if not vectors:
            return

        vectors_np = np.asarray(
            vectors,
            dtype="float32",
        )

        if vectors_np.ndim != 2:
            raise ValueError(
                "vectors must have shape [N, dimension]"
            )

        if vectors_np.shape[1] != self.dimension:
            raise ValueError(
                f"Dimension mismatch. "
                f"Expected {self.dimension}, "
                f"got {vectors_np.shape[1]}"
            )

        self.index.add(vectors_np)

        self.metadata.extend(metadata)

    # ==========================================================
    # SAVE
    # ==========================================================

    def save(
        self,
        directory: str,
        model_name: str,
        normalize: bool = True,
        version: str = "ver_5_x_page_x",
    ):

        directory = Path(directory)

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        index_path = (
            directory / "index.faiss"
        )

        metadata_path = (
            directory / "metadata.json"
        )

        info_path = (
            directory / "info.json"
        )

        # ------------------------------------------------------
        # FAISS
        # ------------------------------------------------------

        faiss.write_index(
            self.index,
            str(index_path),
        )

        # ------------------------------------------------------
        # METADATA
        # ------------------------------------------------------

        with open(
            metadata_path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                self.metadata,
                f,
                ensure_ascii=False,
                indent=2,
            )

        # ------------------------------------------------------
        # INFO
        # ------------------------------------------------------

        info = {
            "version": version,
            "embedding_model": model_name,
            "dimension": self.dimension,
            "normalize": normalize,
            "index_type": "IndexFlatIP",
            "metric": "inner_product",
            "total_vectors": self.index.ntotal,
        }

        with open(
            info_path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                info,
                f,
                ensure_ascii=False,
                indent=2,
            )

    # ==========================================================
    # LOAD
    # ==========================================================

    def load(
        self,
        directory: str,
    ):

        directory = Path(directory)

        index_path = (
            directory / "index.faiss"
        )

        metadata_path = (
            directory / "metadata.json"
        )

        info_path = (
            directory / "info.json"
        )

        # ------------------------------------------------------
        # LOAD FAISS
        # ------------------------------------------------------

        self.index = faiss.read_index(
            str(index_path)
        )

        # ------------------------------------------------------
        # LOAD METADATA
        # ------------------------------------------------------

        with open(
            metadata_path,
            "r",
            encoding="utf-8",
        ) as f:

            self.metadata = json.load(f)

        # ------------------------------------------------------
        # VALIDATION
        # ------------------------------------------------------

        if self.index.ntotal != len(
            self.metadata
        ):

            raise ValueError(
                "FAISS index and metadata "
                "size mismatch: "
                f"{self.index.ntotal} vectors, "
                f"{len(self.metadata)} metadata"
            )

        # ------------------------------------------------------
        # INFO
        # ------------------------------------------------------

        if info_path.exists():

            with open(
                info_path,
                "r",
                encoding="utf-8",
            ) as f:

                info = json.load(f)

            if info["dimension"] != self.dimension:

                raise ValueError(
                    "Dimension mismatch between "
                    "store and info.json"
                )

    # ==========================================================
    # SEARCH
    # ==========================================================

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:

        if self.index.ntotal == 0:
            return []

        query_np = np.asarray(
            [query_vector],
            dtype="float32",
        )

        if query_np.shape[1] != self.dimension:

            raise ValueError(
                f"Query dimension mismatch. "
                f"Expected {self.dimension}, "
                f"got {query_np.shape[1]}"
            )

        # Không yêu cầu top_k > số vector
        top_k = min(
            top_k,
            self.index.ntotal,
        )

        scores, indices = (
            self.index.search(
                query_np,
                top_k,
            )
        )

        results = []

        for score, idx in zip(
            scores[0],
            indices[0],
        ):

            if idx < 0:
                continue

            item = dict(
                self.metadata[idx]
            )

            item["score"] = float(score)
            item["faiss_index"] = int(idx)

            results.append(item)

        return results

    # ==========================================================
    # COUNT
    # ==========================================================

    @property
    def count(self) -> int:

        return self.index.ntotal