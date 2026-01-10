"""
PageGeneral - Modül 2: Query
VectorDB'den istenen formatta tümen listesi çıktısı
"""

import json
from pathlib import Path
from typing import List, Dict, Optional

import sys
sys.path.append(str(Path(__file__).parent.parent))

# PyTorch DLL fix
try:
    import torch
except ImportError:
    pass

from config import OUTPUT_DIR, get_logger
from src.vector_store import VectorStore
from src.registry import BookRegistry

logger = get_logger(__name__)


class DivisionQuery:
    """
    VectorDB'den tümen bilgisi sorgulama.

    Çıktı formatı:
    {
        "id": "parag_5",
        "embedding": [0.0123, -0.98, ...],
        "document": "Full paragraph text here",
        "metadata": {
            "division": ["24", "9"],
            "confidence": 0.95,
            "source_page": 14
        }
    }
    """

    def __init__(self):
        self.vector_store = VectorStore()
        self.registry = BookRegistry()

    def get_all_paragraphs(
        self,
        book_id: str = None,
        only_with_divisions: bool = False,
        include_embeddings: bool = True
    ) -> List[Dict]:
        """
        VectorDB'den tüm paragrafları al.

        Args:
            book_id: Belirli bir kitap (None = hepsi)
            only_with_divisions: Sadece tümen içerenleri getir
            include_embeddings: Embedding'leri dahil et

        Returns:
            İstenen formatta paragraf listesi
        """
        # ChromaDB'den veri çek
        where_filter = {"book_id": book_id} if book_id else None

        results = self.vector_store.collection.get(
            where=where_filter,
            include=["documents", "metadatas", "embeddings"] if include_embeddings else ["documents", "metadatas"]
        )

        if not results or not results["ids"]:
            return []

        paragraphs = []
        for i, doc_id in enumerate(results["ids"]):
            meta = results["metadatas"][i]

            # Division string'i listeye çevir
            division_str = meta.get("division", "")
            divisions = division_str.split(",") if division_str else []

            # Sadece division olanları filtrele
            if only_with_divisions and not divisions:
                continue

            # Embedding al
            embedding = []
            if include_embeddings and results.get("embeddings") is not None:
                emb = results["embeddings"][i]
                embedding = emb.tolist() if hasattr(emb, 'tolist') else list(emb)

            para = {
                "id": f"parag_{i}",
                "embedding": embedding,
                "document": results["documents"][i],
                "metadata": {
                    "division": divisions,
                    "confidence": meta.get("confidence", 0.0),
                    "source_page": meta.get("page", 0)
                }
            }
            paragraphs.append(para)

        return paragraphs

    def get_divisions_summary(self, book_id: str = None) -> Dict:
        """
        Tüm tümenlerin özet listesi.

        Returns:
            {
                "total_paragraphs": 335,
                "paragraphs_with_divisions": 45,
                "divisions": ["5", "9", "24", ...],
                "division_counts": {"5": 12, "9": 8, ...}
            }
        """
        paragraphs = self.get_all_paragraphs(book_id, include_embeddings=False)

        all_divisions = set()
        division_counts = {}
        with_divisions = 0

        for para in paragraphs:
            divs = para["metadata"]["division"]
            if divs:
                with_divisions += 1
                for d in divs:
                    all_divisions.add(d)
                    division_counts[d] = division_counts.get(d, 0) + 1

        return {
            "total_paragraphs": len(paragraphs),
            "paragraphs_with_divisions": with_divisions,
            "divisions": sorted(list(all_divisions), key=lambda x: int(x) if x.isdigit() else 0),
            "division_counts": dict(sorted(division_counts.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0))
        }

    def export_json(
        self,
        output_path: Path = None,
        book_id: str = None,
        only_with_divisions: bool = False,
        include_embeddings: bool = True
    ) -> Dict:
        """
        VectorDB'den JSON export.

        Args:
            output_path: Çıktı dosyası
            book_id: Belirli kitap
            only_with_divisions: Sadece tümen içerenler
            include_embeddings: Embedding dahil

        Returns:
            {"status": "success", "output_file": "...", "count": 45}
        """
        paragraphs = self.get_all_paragraphs(book_id, only_with_divisions, include_embeddings)
        summary = self.get_divisions_summary(book_id)

        output_data = {
            "summary": summary,
            "paragraphs": paragraphs
        }

        if output_path is None:
            suffix = f"_{book_id}" if book_id else ""
            output_path = OUTPUT_DIR / f"divisions_export{suffix}.json"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Export tamamlandi: {output_path}")

        return {
            "status": "success",
            "output_file": str(output_path),
            "total_paragraphs": len(paragraphs),
            "divisions_found": summary["divisions"]
        }

    def list_books(self) -> List[Dict]:
        """Yüklü kitapları listele"""
        return self.registry.list_ready()


# CLI
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="VectorDB'den tümen listesi çıktısı")
    parser.add_argument("--book", "-b", help="Kitap ID")
    parser.add_argument("--output", "-o", help="Çıktı dosyası")
    parser.add_argument("--divisions-only", "-d", action="store_true", help="Sadece tümen içerenler")
    parser.add_argument("--no-embed", action="store_true", help="Embedding olmadan")
    parser.add_argument("--summary", "-s", action="store_true", help="Sadece özet")
    parser.add_argument("--list-books", "-l", action="store_true", help="Kitapları listele")

    args = parser.parse_args()

    query = DivisionQuery()

    if args.list_books:
        books = query.list_books()
        print("\nYüklü Kitaplar:")
        print("=" * 50)
        for book in books:
            print(f"  ID: {book['id']}")
            print(f"  Başlık: {book['title']}")
            print(f"  Paragraf: {book['paragraphs']}")
            print()

    elif args.summary:
        summary = query.get_divisions_summary(args.book)
        print("\nTümen Özeti:")
        print("=" * 50)
        print(f"Toplam paragraf: {summary['total_paragraphs']}")
        print(f"Tümen içeren: {summary['paragraphs_with_divisions']}")
        print(f"Tümenler: {summary['divisions']}")
        print(f"\nTümen sayıları:")
        for div, count in summary['division_counts'].items():
            print(f"  {div}. Tümen: {count} paragraf")

    else:
        result = query.export_json(
            output_path=args.output,
            book_id=args.book,
            only_with_divisions=args.divisions_only,
            include_embeddings=not args.no_embed
        )

        print(f"\n[OK] Export: {result['output_file']}")
        print(f"     Paragraf: {result['total_paragraphs']}")
        print(f"     Tümenler: {result['divisions_found']}")
