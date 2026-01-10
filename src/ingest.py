"""
PageGeneral v2 - Ingest Pipeline
PDF -> Parse -> Embed -> VectorDB
"""

from pathlib import Path
from typing import Optional, Callable
from tqdm import tqdm

import sys
sys.path.append(str(Path(__file__).parent.parent))

from config import INPUT_DIR, get_logger
from src.pdf_parser import PDFParser
from src.registry import BookRegistry, calculate_pdf_hash
from src.vector_store import VectorStore

logger = get_logger(__name__)


class IngestPipeline:
    """
    PDF dosyalarini VectorDB'ye yukleme pipeline'i.

    Akis:
    1. PDF hash check (zaten yuklenmis mi?)
    2. PDF parse (paragraf cikartma)
    3. Registry'ye kayit
    4. Embedding & VectorDB'ye ekleme
    """

    def __init__(self):
        self.parser = PDFParser()
        self.registry = BookRegistry()
        self.vector_store = VectorStore()

    def ingest_pdf(
        self,
        pdf_path: Path,
        book_title: str = None,
        force: bool = False,
        progress_callback: Callable[[str, int], None] = None
    ) -> dict:
        """
        Tek PDF dosyasini isle ve VectorDB'ye ekle.

        Args:
            pdf_path: PDF dosya yolu
            book_title: Kitap adi (None ise dosya adindan alinir)
            force: True ise zaten yuklu olsa bile yeniden yukle
            progress_callback: Progress callback fonksiyonu (message, percent)

        Returns:
            {
                "status": "success" | "skipped" | "error",
                "book_id": "abc123",
                "message": "...",
                "paragraphs": 335,
                "pages": 370
            }
        """
        pdf_path = Path(pdf_path)

        def update_progress(msg: str, percent: int = 0):
            logger.info(msg)
            if progress_callback:
                progress_callback(msg, percent)

        # 1. Dosya kontrol
        if not pdf_path.exists():
            return {
                "status": "error",
                "message": f"Dosya bulunamadi: {pdf_path}",
                "book_id": None
            }

        # 2. Hash check - zaten yuklenmis mi?
        book_id = calculate_pdf_hash(pdf_path)
        update_progress(f"Kontrol ediliyor: {pdf_path.name}", 5)

        if not force and self.registry.exists_by_id(book_id):
            existing = self.registry.get(book_id)
            if existing and existing.get("status") == "ready":
                return {
                    "status": "skipped",
                    "message": f"Kitap zaten yuklu: {pdf_path.name}",
                    "book_id": book_id,
                    "paragraphs": existing.get("paragraphs", 0),
                    "pages": existing.get("pages", 0)
                }

        # Force modda eski kayitlari temizle
        if force and self.registry.exists_by_id(book_id):
            update_progress("Eski kayitlar temizleniyor...", 10)
            self.vector_store.delete_book(book_id)
            self.registry.delete(book_id)

        # 3. PDF Parse
        update_progress(f"PDF parse ediliyor: {pdf_path.name}", 15)

        try:
            parse_result = self.parser.parse(pdf_path)

            if parse_result["status"] == "error":
                return {
                    "status": "error",
                    "message": f"Parse hatasi: {parse_result.get('error', 'Bilinmeyen hata')}",
                    "book_id": book_id
                }

            paragraphs = parse_result.get("paragraphs", [])
            num_pages = parse_result.get("pages", 0)

            if not paragraphs:
                return {
                    "status": "error",
                    "message": "PDF'den paragraf cikarilamadi",
                    "book_id": book_id
                }

            update_progress(f"{len(paragraphs)} paragraf cikarildi", 30)

        except Exception as e:
            logger.error(f"Parse hatasi: {e}")
            return {
                "status": "error",
                "message": f"Parse hatasi: {str(e)}",
                "book_id": book_id
            }

        # 4. Registry'ye kayit (status: processing)
        title = book_title or pdf_path.stem
        self.registry.add(pdf_path, {
            "title": title,
            "pages": num_pages,
            "paragraphs": len(paragraphs)
        })
        self.registry.update_status(book_id, "processing")
        update_progress("Registry'ye kaydedildi", 35)

        # 5. Paragraf metadata ekle
        for i, para in enumerate(paragraphs):
            para["book_name"] = title
            para["para_index"] = i

        # 6. VectorDB'ye ekle (embedding + insert)
        update_progress(f"Embedding olusturuluyor ({len(paragraphs)} paragraf)...", 40)

        try:
            added_count = self.vector_store.add_book(book_id, paragraphs)
            update_progress(f"VectorDB'ye eklendi: {added_count} paragraf", 90)

        except Exception as e:
            logger.error(f"VectorDB hatasi: {e}")
            self.registry.update_status(book_id, "error")
            return {
                "status": "error",
                "message": f"VectorDB hatasi: {str(e)}",
                "book_id": book_id
            }

        # 7. Registry guncelle (status: ready)
        self.registry.update_status(book_id, "ready")
        update_progress(f"Tamamlandi: {pdf_path.name}", 100)

        return {
            "status": "success",
            "message": f"Basariyla yuklendi: {title}",
            "book_id": book_id,
            "paragraphs": len(paragraphs),
            "pages": num_pages
        }

    def ingest_folder(
        self,
        folder_path: Path = None,
        force: bool = False,
        progress_callback: Callable[[str, int, int, int], None] = None
    ) -> dict:
        """
        Klasordeki tum PDF'leri isle.

        Args:
            folder_path: Klasor yolu (None ise INPUT_DIR)
            force: Zaten yuklu olanlari da yeniden yukle
            progress_callback: Progress callback (message, current, total, percent)

        Returns:
            {
                "status": "success",
                "processed": 5,
                "skipped": 2,
                "errors": 1,
                "results": [...]
            }
        """
        folder_path = Path(folder_path) if folder_path else INPUT_DIR

        if not folder_path.exists():
            return {
                "status": "error",
                "message": f"Klasor bulunamadi: {folder_path}",
                "processed": 0,
                "skipped": 0,
                "errors": 0,
                "results": []
            }

        pdf_files = list(folder_path.glob("*.pdf"))

        if not pdf_files:
            return {
                "status": "success",
                "message": f"Klasorde PDF bulunamadi: {folder_path}",
                "processed": 0,
                "skipped": 0,
                "errors": 0,
                "results": []
            }

        results = []
        processed = 0
        skipped = 0
        errors = 0

        logger.info(f"{len(pdf_files)} PDF bulundu, isleniyor...")

        for i, pdf_file in enumerate(tqdm(pdf_files, desc="PDF'ler isleniyor")):
            if progress_callback:
                percent = int((i / len(pdf_files)) * 100)
                progress_callback(f"Isleniyor: {pdf_file.name}", i + 1, len(pdf_files), percent)

            result = self.ingest_pdf(pdf_file, force=force)
            results.append(result)

            if result["status"] == "success":
                processed += 1
            elif result["status"] == "skipped":
                skipped += 1
            else:
                errors += 1

        logger.info(f"Tamamlandi: {processed} islendi, {skipped} atlandi, {errors} hata")

        return {
            "status": "success",
            "message": f"{processed} kitap yuklendi",
            "processed": processed,
            "skipped": skipped,
            "errors": errors,
            "results": results
        }

    def get_stats(self) -> dict:
        """Pipeline istatistikleri"""
        registry_stats = self.registry.get_stats()
        vector_stats = self.vector_store.get_total_stats()

        return {
            "registry": registry_stats,
            "vectordb": vector_stats
        }


# Kolay kullanim icin fonksiyonlar
def ingest_pdf(pdf_path: Path, **kwargs) -> dict:
    """Tek PDF yukle"""
    pipeline = IngestPipeline()
    return pipeline.ingest_pdf(pdf_path, **kwargs)


def ingest_folder(folder_path: Path = None, **kwargs) -> dict:
    """Klasordeki tum PDF'leri yukle"""
    pipeline = IngestPipeline()
    return pipeline.ingest_folder(folder_path, **kwargs)


# CLI
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PDF Ingest Pipeline")
    parser.add_argument("path", nargs="?", help="PDF dosyasi veya klasor yolu")
    parser.add_argument("--force", "-f", action="store_true", help="Zaten yuklu olanlari yeniden yukle")

    args = parser.parse_args()

    pipeline = IngestPipeline()

    if args.path:
        path = Path(args.path)
        if path.is_file():
            result = pipeline.ingest_pdf(path, force=args.force)
        else:
            result = pipeline.ingest_folder(path, force=args.force)
    else:
        # Default: INPUT_DIR
        result = pipeline.ingest_folder(force=args.force)

    print("\n" + "=" * 50)
    print("SONUC:")
    print("=" * 50)

    if result["status"] == "success":
        print(f"Islenen: {result.get('processed', 0)}")
        print(f"Atlanan: {result.get('skipped', 0)}")
        print(f"Hata: {result.get('errors', 0)}")
    else:
        print(f"Durum: {result['status']}")
        print(f"Mesaj: {result.get('message', '')}")

    print("\nIstatistikler:")
    stats = pipeline.get_stats()
    print(f"  Registry: {stats['registry']}")
    print(f"  VectorDB: {stats['vectordb']}")
