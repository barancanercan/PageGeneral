"""
PAGEGENERAL - Vector Store
Embeddings + Chromadb Storage + Semantic Search
"""

import chromadb
from sentence_transformers import SentenceTransformer
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from typing import List, Dict
import json


class VectorStore:
    """Chromadb-based vector storage"""

    def __init__(self, persist_dir: str = None):
        self.persist_dir = persist_dir or str(config.CHROMA_DB_DIR)
        self.client = chromadb.Client()

        # Embedding model
        if config.VERBOSE:
            print(f"🔧 Embedding model yükleniyor: {config.EMBEDDING_MODEL_NAME}")

        self.embedder = SentenceTransformer(config.EMBEDDING_MODEL_NAME)

        if config.VERBOSE:
            print(f"✅ Embedder ready (dim: {config.EMBEDDING_DIMENSION})")

    def create_collections(self, divisions: List[str]):
        """Her tümen için collection oluştur"""

        if config.VERBOSE:
            print(f"\n📦 Collections oluşturuluyor ({len(divisions)} tümen)...\n")

        for division in divisions:
            col_name = self._sanitize_name(division)

            try:
                self.client.delete_collection(name=col_name)
            except:
                pass

            self.client.create_collection(
                name=col_name,
                metadata={"hnsw:space": "cosine"}
            )

            if config.VERBOSE:
                print(f"  ✅ {division} → {col_name}")

    def ingest_chunks(self, chunks: List[Dict]):
        """Chunks'ları Chromadb'ye yükle"""

        if config.VERBOSE:
            print(f"\n🔗 {len(chunks)} chunk Chromadb'ye yükleniyor...\n")

        # Tüm divisions'u topla
        all_divisions = set()
        for chunk in chunks:
            # Division'ı sanitize et (liste ise string'e çevir)
            divisions = chunk["metadata"].get("division", [])

            if isinstance(divisions, list):
                division_str = ", ".join(divisions)
            else:
                division_str = divisions

            # Metadata'yı sanitize et
            chunk["metadata"]["division"] = division_str

            # Tüm divisions'u topla
            if isinstance(divisions, list):
                for div in divisions:
                    all_divisions.add(div)
            else:
                for div in divisions.split(","):
                    all_divisions.add(div.strip())

        # Collections oluştur
        self.create_collections(list(all_divisions))

        # Her chunk'ı embed et ve kaydet
        for chunk_idx, chunk in enumerate(chunks):
            text = chunk["document"]
            embedding = self.embedder.encode(text).tolist()

            # Division string'dir artık
            division_str = chunk["metadata"]["division"]

            # Her tümene ekle (split et)
            divisions_list = [d.strip() for d in division_str.split(",")]

            for division in divisions_list:
                col_name = self._sanitize_name(division)
                collection = self.client.get_collection(col_name)

                # Metadata'yı copy et (değişmeden)
                metadata = chunk["metadata"].copy()

                collection.add(
                    ids=[chunk["id"]],
                    embeddings=[embedding],
                    documents=[text],
                    metadatas=[metadata]  # ← STRING division!
                )

            if config.VERBOSE and (chunk_idx + 1) % 10 == 0:
                print(f"  ✓ {chunk_idx + 1}/{len(chunks)} chunks processed")

        if config.VERBOSE:
            print(f"\n✅ Tüm chunks Chromadb'ye yüklendi")

    def search(self, query_text: str, division: str, top_k: int = 5):
        """
        Division'da semantic search

        Args:
            query_text: Sorgu metni
            division: Hangi tümende arasın?
            top_k: Kaç sonuç dönsün?

        Returns:
            {
                "ids": [...],
                "documents": [...],
                "embeddings": [...],
                "metadatas": [...],
                "distances": [...]
            }
        """

        col_name = self._sanitize_name(division)

        try:
            collection = self.client.get_collection(col_name)
        except Exception as e:
            if config.VERBOSE:
                print(f"❌ Collection bulunamadı: {division}")
            return {"ids": [], "documents": [], "metadatas": []}

        # Query embedding
        query_embedding = self.embedder.encode(query_text).tolist()

        # Chromadb search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["embeddings", "documents", "metadatas", "distances"]
        )

        return results

    def format_results_berke(self, search_results: Dict) -> List[Dict]:
        """Chromadb results → Berke formatı (division'ı string'den listeye çevir)"""
        formatted = []

        if not search_results["ids"] or not search_results["ids"][0]:
            return formatted

        for i, doc_id in enumerate(search_results["ids"][0]):
            metadata = search_results["metadatas"][0][i]

            # Division string'den listeye çevir
            division_str = metadata.get("division", "")
            division_list = [d.strip() for d in division_str.split(",")] if division_str else []

            # Metadata'yı Berke formatına düzelt
            metadata["division"] = division_list

            result = {
                "id": doc_id,
                "embedding": search_results["embeddings"][0][i] if search_results["embeddings"] else [],
                "document": search_results["documents"][0][i],
                "metadata": metadata
            }
            formatted.append(result)

        return formatted

    def get_division_stats(self):
        """Tüm collections'un istatistikleri"""

        stats = {}

        try:
            collections = self.client.list_collections()

            for col in collections:
                col_name = col.name
                collection = self.client.get_collection(col_name)

                # Count
                try:
                    count = collection.count()
                    stats[col_name] = count
                except:
                    stats[col_name] = 0

            return stats
        except Exception as e:
            if config.VERBOSE:
                print(f"⚠️  Stats hatası: {e}")
            return {}

    def _sanitize_name(self, division: str) -> str:
        """Division adını collection adına dönüştür (Turkish → ASCII)"""

        # Türkçe karakterleri ASCII'ye dönüştür
        turkish_map = {
            'ü': 'u', 'ö': 'o', 'ş': 's', 'ç': 'c', 'ğ': 'g', 'ı': 'i',
            'Ü': 'U', 'Ö': 'O', 'Ş': 'S', 'Ç': 'C', 'Ğ': 'G', 'İ': 'I'
        }

        name = division.lower()

        # Türkçe karakterleri değiştir
        for tr_char, en_char in turkish_map.items():
            name = name.replace(tr_char, en_char)

        # Boşluk → underscore, nokta sil
        name = name.replace(" ", "_").replace(".", "")

        # Sadece allowed chars: a-z0-9._-
        name = "".join(c if c.isalnum() or c in "_-." else "" for c in name)

        # Chromadb: 3-512 chars, with [a-zA-Z0-9._-]
        if len(name) < 3:
            name = name + "_" * (3 - len(name))

        return name[:63]


def test_vector_store():
    """Test: vector store çalışıyor mu?"""

    print("🧪 Vector Store Test\n")

    # Mock chunks
    mock_chunks = [
        {
            "id": "parag_5",
            "document": "4. Piyade Tümeni komutanı cepheye gitmek üzere hazırlanıyordu.",
            "metadata": {
                "division": ["4. Piyade Tümeni"],
                "confidence": 0.95,
                "source_page": 14,
                "book_name": "Test Kitap",
                "book_id": "test_book"
            }
        },
        {
            "id": "parag_15",
            "document": "9. Piyade Tümeni ile 24. Piyade Tümeni ortak operasyon yapacaklardı.",
            "metadata": {
                "division": ["9. Piyade Tümeni", "24. Piyade Tümeni"],
                "confidence": 0.92,
                "source_page": 18,
                "book_name": "Test Kitap",
                "book_id": "test_book"
            }
        }
    ]

    # Vector store oluştur
    vs = VectorStore()

    # Ingest
    print("📥 Chunks yükleniyor...")
    vs.ingest_chunks(mock_chunks)

    # Stats
    print("\n📊 İstatistikler:")
    stats = vs.get_division_stats()
    for col, count in stats.items():
        print(f"  {col}: {count} chunks")

    # Search test
    print("\n🔍 Search test...")
    query = "Hangi tümen cepheye gitti?"

    for division in ["4. Piyade Tümeni", "9. Piyade Tümeni"]:
        print(f"\n  Division: {division}")
        results = vs.search(query, division, top_k=2)

        formatted = vs.format_results_berke(results)

        for r in formatted:
            print(f"    - {r['id']}: {r['document'][:60]}...")
            print(f"      Meta: {r['metadata']}")

    print("\n✅ Test tamamlandı")


if __name__ == "__main__":
    test_vector_store()