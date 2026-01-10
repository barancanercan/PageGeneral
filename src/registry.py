"""
PageGeneral v2 - Book Registry
Kitap kayit sistemi ve duplicate detection
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

import sys
sys.path.append(str(Path(__file__).parent.parent))

from config import REGISTRY_FILE, get_logger

logger = get_logger(__name__)


def calculate_pdf_hash(pdf_path: Path) -> str:
    """PDF dosyasinin MD5 hash'ini hesapla (ilk 12 karakter)"""
    return hashlib.md5(pdf_path.read_bytes()).hexdigest()[:12]


class BookRegistry:
    """
    Kitap kayit sistemi.
    Hangi kitaplarin islendigi takip edilir, tekrar isleme engellenir.
    """

    def __init__(self, registry_path: Path = None):
        self.registry_path = registry_path or REGISTRY_FILE
        self._ensure_registry_exists()

    def _ensure_registry_exists(self):
        """Registry dosyasinin var oldugunu garanti et"""
        if not self.registry_path.exists():
            self._save({"books": []})
            logger.info(f"Registry olusturuldu: {self.registry_path}")

    def _load(self) -> dict:
        """Registry'i oku"""
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save(self, data: dict):
        """Registry'i kaydet"""
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def exists(self, pdf_path: Path) -> bool:
        """PDF zaten islenmis mi kontrol et (hash bazli)"""
        book_hash = calculate_pdf_hash(pdf_path)
        data = self._load()
        return any(book["id"] == book_hash for book in data["books"])

    def exists_by_id(self, book_id: str) -> bool:
        """Book ID ile var mi kontrol et"""
        data = self._load()
        return any(book["id"] == book_id for book in data["books"])

    def add(self, pdf_path: Path, metadata: dict = None) -> str:
        """
        Yeni kitap ekle.

        Args:
            pdf_path: PDF dosya yolu
            metadata: Ek metadata (title, pages, paragraphs vb.)

        Returns:
            book_id (MD5 hash)
        """
        book_id = calculate_pdf_hash(pdf_path)

        # Zaten var mi kontrol et
        if self.exists_by_id(book_id):
            logger.warning(f"Kitap zaten mevcut: {pdf_path.name} (ID: {book_id})")
            return book_id

        # Yeni kitap kaydi
        book_entry = {
            "id": book_id,
            "filename": pdf_path.name,
            "title": metadata.get("title", pdf_path.stem) if metadata else pdf_path.stem,
            "pages": metadata.get("pages", 0) if metadata else 0,
            "paragraphs": metadata.get("paragraphs", 0) if metadata else 0,
            "ingested_at": datetime.now().isoformat(),
            "status": "pending"  # pending | processing | ready | error
        }

        data = self._load()
        data["books"].append(book_entry)
        self._save(data)

        logger.info(f"Kitap eklendi: {pdf_path.name} (ID: {book_id})")
        return book_id

    def get(self, book_id: str) -> Optional[dict]:
        """Book ID ile kitap bilgisi getir"""
        data = self._load()
        for book in data["books"]:
            if book["id"] == book_id:
                return book
        return None

    def get_by_filename(self, filename: str) -> Optional[dict]:
        """Dosya adi ile kitap bilgisi getir"""
        data = self._load()
        for book in data["books"]:
            if book["filename"] == filename:
                return book
        return None

    def list_all(self) -> List[dict]:
        """Tum kitaplari listele"""
        data = self._load()
        return data["books"]

    def list_ready(self) -> List[dict]:
        """Sadece 'ready' durumundaki kitaplari listele"""
        return [b for b in self.list_all() if b["status"] == "ready"]

    def update_status(self, book_id: str, status: str) -> bool:
        """
        Kitap durumunu guncelle.

        Args:
            book_id: Kitap ID
            status: Yeni durum (pending | processing | ready | error)

        Returns:
            Basarili mi
        """
        data = self._load()
        for book in data["books"]:
            if book["id"] == book_id:
                book["status"] = status
                self._save(data)
                logger.info(f"Kitap durumu guncellendi: {book_id} -> {status}")
                return True
        return False

    def update_metadata(self, book_id: str, metadata: dict) -> bool:
        """Kitap metadata'sini guncelle"""
        data = self._load()
        for book in data["books"]:
            if book["id"] == book_id:
                book.update(metadata)
                self._save(data)
                logger.info(f"Kitap metadata guncellendi: {book_id}")
                return True
        return False

    def delete(self, book_id: str) -> bool:
        """Kitabi registry'den sil"""
        data = self._load()
        original_count = len(data["books"])
        data["books"] = [b for b in data["books"] if b["id"] != book_id]

        if len(data["books"]) < original_count:
            self._save(data)
            logger.info(f"Kitap silindi: {book_id}")
            return True
        return False

    def get_stats(self) -> dict:
        """Registry istatistikleri"""
        books = self.list_all()
        return {
            "total_books": len(books),
            "ready": sum(1 for b in books if b["status"] == "ready"),
            "pending": sum(1 for b in books if b["status"] == "pending"),
            "processing": sum(1 for b in books if b["status"] == "processing"),
            "error": sum(1 for b in books if b["status"] == "error"),
            "total_pages": sum(b.get("pages", 0) for b in books),
            "total_paragraphs": sum(b.get("paragraphs", 0) for b in books)
        }


# Test
if __name__ == "__main__":
    registry = BookRegistry()
    print("Registry Stats:", registry.get_stats())
    print("All Books:", registry.list_all())
