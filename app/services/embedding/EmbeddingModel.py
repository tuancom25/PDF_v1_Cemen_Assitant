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

from abc import ABC, abstractmethod
class EmbeddingModel(ABC):

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass

    @abstractmethod
    def embed(
        self,
        texts: list[str]
    ) -> list[list[float]]:
        pass

from app.services .chunking.chunk import Chunk


class EmbeddingBuffer:

    def __init__(self, batch_size: int = 128):
        self.batch_size = batch_size
        self._items: list[Chunk] = []

    def add(self, chunk: Chunk) -> None:
        self._items.append(chunk)

    def add_many(
        self,
        chunks: list[Chunk]
    ) -> None:

        self._items.extend(chunks)

    def is_ready(self) -> bool:
        return len(self._items) >= self.batch_size

    def pop_batch(self) -> list[Chunk]:

        if not self._items:
            return []

        batch = self._items[:self.batch_size]

        del self._items[:self.batch_size]

        return batch

    def flush(self) -> list[Chunk]:

        batch = self._items

        self._items = []

        return batch

    def __len__(self):
        return len(self._items)


class VectorStore(ABC):

    @abstractmethod
    def add(
        self,
        chunks: list[Chunk],
        vectors: list[list[float]]
    ) -> None:
        pass