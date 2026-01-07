"""
PAGEGENERAL - Smart Chunker
Extraction sonuçlarından → Chunks + Metadata (Berke formatı)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from datetime import datetime
from typing import List, Dict


class SmartChunker:
    """Extraction → Chunks with metadata"""

    def __init__(self, book_name: str, book_id: str):
        self.book_name = book_name
        self.book_id = book_id

    def create_chunks(self, extraction_results: List[Dict], chunk_size: int = 512):
        """
        Extraction'dan chunks yap + Berke formatında metadata ekle

        Args:
            extraction_results: Division Extractor output
            chunk_size: Token cinsinden chunk boyutu

        Returns:
            List[{
                "id": "parag_5",
                "document": "...",
                "metadata": {
                    "division": ["4. Piyade Tümeni"],
                    "confidence": 0.95,
                    "source_page": 14,
                    "book_name": "...",
                    "book_id": "..."
                }
            }]
        """

        chunks = []

        for result in extraction_results:
            # Confidence filter
            if result["confidence"] < config.EXTRACTION_CONFIDENCE_THRESHOLD:
                continue

            # Boş division skip et
            if not result["divisions"]:
                continue

            para_id = result["para_id"]
            chunk_id = f"parag_{para_id}"

            # Metadata oluştur
            metadata = {
                "division": ", ".join(result["divisions"]),  # ← STRING (DOĞRU!)
                "confidence": result["confidence"],
                "source_page": self._calculate_page(para_id),
                "book_name": self.book_name,
                "book_id": self.book_id,
                "para_id": para_id,
                "timestamp": datetime.now().isoformat()
            }

            # Chunk oluştur (Berke formatı)
            chunk = {
                "id": chunk_id,
                "document": result["text"],
                "metadata": metadata
            }

            chunks.append(chunk)

        if config.VERBOSE:
            print(f"✂️  {len(chunks)} chunk oluşturuldu")

        return chunks

    def _calculate_page(self, para_id: int) -> int:
        """Para ID'den sayfa numarasını bul (basit: 50 para/sayfa)"""
        return (para_id // 50) + 1


def test_chunker():
    """Test: chunking çalışıyor mu?"""

    print("🧪 Smart Chunker Test\n")

    # Mock extraction results
    mock_results = [
        {
            "para_id": 5,
            "text": "4. Piyade Tümeni komutanı, cepheye gitmek üzere hazırlanıyordu.",
            "divisions": ["4. Piyade Tümeni"],
            "confidence": 0.95
        },
        {
            "para_id": 15,
            "text": "9. Piyade Tümeni ile 24. Piyade Tümeni ortak operasyon yapacaklardı.",
            "divisions": ["9. Piyade Tümeni", "24. Piyade Tümeni"],
            "confidence": 0.92
        },
        {
            "para_id": 20,
            "text": "Hava çok soğuktu.",
            "divisions": [],  # No division
            "confidence": 0.0
        }
    ]

    chunker = SmartChunker(
        book_name="Türk İstiklal Harbi - Mondros Mütarekesi",
        book_id="turk_istiklal_harbi_mondros"
    )

    chunks = chunker.create_chunks(mock_results)

    print(f"📊 {len(chunks)} chunk oluşturuldu\n")

    for i, chunk in enumerate(chunks, 1):
        print(f"Chunk {i}:")
        print(f"  ID: {chunk['id']}")
        print(f"  Divisions: {chunk['metadata']['division']}")
        print(f"  Confidence: {chunk['metadata']['confidence']:.0%}")
        print(f"  Page: {chunk['metadata']['source_page']}")
        print(f"  Text: {chunk['document'][:60]}...")
        print()

    print("✅ Test tamamlandı")


if __name__ == "__main__":
    test_chunker()