"""
PageGeneral v2 - Embedder
Sentence Transformers ile metin embedding
"""

from typing import List, Union
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))

from config import EMBEDDING_MODEL, EMBEDDING_BATCH_SIZE, get_logger

logger = get_logger(__name__)

# Lazy loading - model sadece ihtiyac olunca yuklenir
_model = None


def get_model():
    """Embedding modelini yukle (lazy loading)"""
    global _model
    if _model is None:
        logger.info(f"Embedding model yukleniyor: {EMBEDDING_MODEL}")
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info("Embedding model yuklendi")
    return _model


class Embedder:
    """
    Metin embedding sinifi.
    Sentence Transformers kullanarak metinleri vektore donusturur.
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or EMBEDDING_MODEL
        self._model = None

    @property
    def model(self):
        """Lazy model loading"""
        if self._model is None:
            logger.info(f"Embedding model yukleniyor: {self.model_name}")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            logger.info("Embedding model yuklendi")
        return self._model

    def embed(self, texts: Union[str, List[str]], batch_size: int = None) -> List[List[float]]:
        """
        Metin veya metin listesini embedding'e donustur.

        Args:
            texts: Tek metin veya metin listesi
            batch_size: Batch boyutu (default: config'den)

        Returns:
            Embedding listesi (her biri float listesi)
        """
        batch_size = batch_size or EMBEDDING_BATCH_SIZE

        # Tek metin ise listeye cevir
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return []

        logger.info(f"{len(texts)} metin embedding'e donusturuluyor...")

        # Embedding olustur
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 10,
            convert_to_numpy=True
        )

        # numpy array'i liste'ye cevir
        result = embeddings.tolist()
        logger.info(f"Embedding tamamlandi: {len(result)} vektor")

        return result

    def embed_single(self, text: str) -> List[float]:
        """Tek metin icin embedding"""
        result = self.embed([text])
        return result[0] if result else []

    def get_embedding_dimension(self) -> int:
        """Embedding boyutunu dondur"""
        return self.model.get_sentence_embedding_dimension()


# Kolay kullanim icin global fonksiyonlar
def embed_texts(texts: Union[str, List[str]], batch_size: int = None) -> List[List[float]]:
    """Global embedder ile embedding olustur"""
    embedder = Embedder()
    return embedder.embed(texts, batch_size)


def embed_single(text: str) -> List[float]:
    """Tek metin icin embedding"""
    embedder = Embedder()
    return embedder.embed_single(text)


# Test
if __name__ == "__main__":
    print("Testing Embedder...")

    # Test texts
    test_texts = [
        "Bu bir test cumesidir.",
        "5 nci Kafkas Tumeni Sarikamis'a konuslanmistir.",
        "Turk Istiklal Harbi onemli bir donemdir."
    ]

    embedder = Embedder()
    embeddings = embedder.embed(test_texts)

    print(f"Embedding dimension: {embedder.get_embedding_dimension()}")
    print(f"Number of embeddings: {len(embeddings)}")
    print(f"First embedding (first 5 values): {embeddings[0][:5]}")
