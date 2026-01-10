"""
PageGeneral v2 - Vector Store
ChromaDB ile vector storage ve semantic search
"""

from typing import List, Dict, Optional
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))

from config import VECTORDB_DIR, CHROMA_COLLECTION_NAME, DEFAULT_TOP_K, get_logger
from src.embedder import Embedder

logger = get_logger(__name__)


class VectorStore:
    """
    ChromaDB wrapper sinifi.
    Paragraf embedding'lerini saklar ve semantic search yapar.
    """

    def __init__(self, persist_dir: Path = None, collection_name: str = None):
        self.persist_dir = persist_dir or VECTORDB_DIR
        self.collection_name = collection_name or CHROMA_COLLECTION_NAME
        self._client = None
        self._collection = None
        self._embedder = None

    @property
    def embedder(self) -> Embedder:
        """Lazy embedder loading"""
        if self._embedder is None:
            self._embedder = Embedder()
        return self._embedder

    @property
    def client(self):
        """Lazy ChromaDB client loading"""
        if self._client is None:
            import chromadb
            from chromadb.config import Settings

            self._client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=Settings(anonymized_telemetry=False)
            )
            logger.info(f"ChromaDB client olusturuldu: {self.persist_dir}")
        return self._client

    @property
    def collection(self):
        """Lazy collection loading"""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "PageGeneral document paragraphs"}
            )
            logger.info(f"Collection yuklendi: {self.collection_name}")
        return self._collection

    def add_book(self, book_id: str, paragraphs: List[Dict]) -> int:
        """
        Kitap paragraflarini VectorDB'ye ekle.

        Args:
            book_id: Kitap ID (hash)
            paragraphs: Paragraf listesi, her biri:
                {
                    "text": "Paragraf metni...",
                    "page": 241,
                    "para_index": 5,
                    "book_name": "Kitap Adi"  # opsiyonel
                }

        Returns:
            Eklenen paragraf sayisi
        """
        if not paragraphs:
            logger.warning(f"Eklenecek paragraf yok: {book_id}")
            return 0

        # ID'ler, metinler ve metadata'lar
        ids = []
        documents = []
        metadatas = []

        for i, para in enumerate(paragraphs):
            para_id = f"{book_id}_para_{i}"
            ids.append(para_id)
            documents.append(para["text"])

            # Division bilgisini string'e çevir (ChromaDB list desteklemiyor)
            divisions = para.get("division", [])
            division_str = ",".join(divisions) if divisions else ""

            metadatas.append({
                "book_id": book_id,
                "book_name": para.get("book_name", ""),
                "page": para.get("page", 0),
                "para_index": para.get("para_index", i),
                "division": division_str,
                "confidence": para.get("confidence", 0.0)
            })

        # Embedding'leri olustur
        logger.info(f"{len(documents)} paragraf icin embedding olusturuluyor...")
        embeddings = self.embedder.embed(documents)

        # ChromaDB'ye ekle
        logger.info(f"ChromaDB'ye ekleniyor: {len(ids)} paragraf")
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        logger.info(f"Kitap eklendi: {book_id} ({len(ids)} paragraf)")
        return len(ids)

    def search(
        self,
        query: str,
        book_ids: List[str] = None,
        top_k: int = None
    ) -> List[Dict]:
        """
        Semantic search yap.

        Args:
            query: Arama sorgusu
            book_ids: Sadece bu kitaplarda ara (None = hepsi)
            top_k: Dondurulecek sonuc sayisi

        Returns:
            Sonuc listesi:
            [
                {
                    "id": "book1_para_5",
                    "text": "Paragraf metni...",
                    "book_id": "abc123",
                    "book_name": "Kitap Adi",
                    "page": 241,
                    "para_index": 5,
                    "distance": 0.15
                }
            ]
        """
        top_k = top_k or DEFAULT_TOP_K

        # Query embedding
        query_embedding = self.embedder.embed_single(query)

        # Where filter (kitap bazli)
        where_filter = None
        if book_ids:
            if len(book_ids) == 1:
                where_filter = {"book_id": book_ids[0]}
            else:
                where_filter = {"book_id": {"$in": book_ids}}

        # Search
        logger.info(f"Arama yapiliyor: '{query[:50]}...' (top_k={top_k})")
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        # Sonuclari formatla
        formatted_results = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                meta = results["metadatas"][0][i]
                # Division string'i listeye çevir
                division_str = meta.get("division", "")
                divisions = division_str.split(",") if division_str else []

                formatted_results.append({
                    "id": doc_id,
                    "text": results["documents"][0][i],
                    "book_id": meta.get("book_id", ""),
                    "book_name": meta.get("book_name", ""),
                    "page": meta.get("page", 0),
                    "para_index": meta.get("para_index", 0),
                    "division": divisions,
                    "confidence": meta.get("confidence", 0.0),
                    "distance": results["distances"][0][i] if results["distances"] else 0
                })

        logger.info(f"Arama tamamlandi: {len(formatted_results)} sonuc")
        return formatted_results

    def delete_book(self, book_id: str) -> bool:
        """Kitabi VectorDB'den sil"""
        try:
            # Bu kitaba ait tum ID'leri bul
            results = self.collection.get(
                where={"book_id": book_id},
                include=[]
            )

            if results and results["ids"]:
                self.collection.delete(ids=results["ids"])
                logger.info(f"Kitap silindi: {book_id} ({len(results['ids'])} paragraf)")
                return True
            else:
                logger.warning(f"Silinecek kitap bulunamadi: {book_id}")
                return False
        except Exception as e:
            logger.error(f"Kitap silme hatasi: {e}")
            return False

    def get_book_stats(self, book_id: str) -> Dict:
        """Kitap istatistikleri"""
        results = self.collection.get(
            where={"book_id": book_id},
            include=["metadatas"]
        )

        if not results or not results["ids"]:
            return {"paragraph_count": 0, "pages": []}

        pages = set()
        for meta in results["metadatas"]:
            if meta.get("page"):
                pages.add(meta["page"])

        return {
            "paragraph_count": len(results["ids"]),
            "pages": sorted(list(pages)),
            "page_count": len(pages)
        }

    def get_total_stats(self) -> Dict:
        """Toplam VectorDB istatistikleri"""
        count = self.collection.count()
        return {
            "total_paragraphs": count,
            "collection_name": self.collection_name
        }

    def book_exists(self, book_id: str) -> bool:
        """Kitap VectorDB'de var mi kontrol et"""
        results = self.collection.get(
            where={"book_id": book_id},
            limit=1,
            include=[]
        )
        return bool(results and results["ids"])


# Test
if __name__ == "__main__":
    print("Testing VectorStore...")

    # Test paragraphs
    test_paragraphs = [
        {
            "text": "5 nci Kafkas Tumeni Sarikamis'ta konuslanmistir.",
            "page": 100,
            "para_index": 0,
            "book_name": "Test Kitap"
        },
        {
            "text": "11 nci Kafkas Tumeni Erzurum'da gorev yapmaktadir.",
            "page": 101,
            "para_index": 1,
            "book_name": "Test Kitap"
        }
    ]

    store = VectorStore()
    print(f"Total stats: {store.get_total_stats()}")

    # Add test book
    count = store.add_book("test123", test_paragraphs)
    print(f"Added {count} paragraphs")

    # Search
    results = store.search("Kafkas Tumeni konuslari", top_k=5)
    print(f"Search results: {len(results)}")
    for r in results:
        print(f"  - Page {r['page']}: {r['text'][:50]}...")
