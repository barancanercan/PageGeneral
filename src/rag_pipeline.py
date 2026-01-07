"""
PAGEGENERAL - RAG Pipeline (Day 2)
PDF → LLM Extraction → Chromadb
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pdf_parser import PDFParser
from src.division_extractor import DivisionExtractor
from src.chunker import SmartChunker
from src.vector_store import VectorStore
from src.llm import OllamaClient
import config
import json
from datetime import datetime


class RAGPipeline:
    """Ana RAG sistemi: PDF → LLM Extraction → Chromadb"""

    def __init__(self, book_name: str, book_id: str):
        self.book_name = book_name
        self.book_id = book_id

        self.parser = PDFParser()
        self.extractor = DivisionExtractor(config.DIVISION_LIST)
        self.chunker = SmartChunker(book_name, book_id)
        self.vs = VectorStore()
        self.llm = OllamaClient()

    def ingest_pdf(self, pdf_path: str | Path) -> dict:
        """
        Tüm pipeline: PDF → Chromadb

        Args:
            pdf_path: PDF dosyasının yolu

        Returns:
            {
                "status": "success" | "error",
                "divisions_found": ["4. Piyade Tümeni", ...],
                "total_paragraphs": 150,
                "chunks_created": 120,
                "error": (varsa)
            }
        """
        pdf_path = Path(pdf_path)

        try:
            # 1. PDF parse
            if config.VERBOSE:
                print(f"\n📄 ADIM 1: PDF Parse Ediliyor...")

            parse_result = self.parser.parse(pdf_path)

            if parse_result['status'] != 'success':
                return {
                    "status": "error",
                    "error": parse_result.get('error')
                }

            content = parse_result['content']

            # 2. Paragraf böl
            if config.VERBOSE:
                print(f"\n✂️  ADIM 2: Paragraf Bölünüyor...")

            paragraphs = content.split('\n\n')
            paragraphs = [p.strip() for p in paragraphs if p.strip()]

            if config.VERBOSE:
                print(f"   {len(paragraphs)} paragraf bulundu")

            # 3. LLM-based extraction
            if config.VERBOSE:
                print(f"\n🤖 ADIM 3: LLM ile Division Extraction...")

            extraction_results = self.extractor.extract(paragraphs, verbose=True)

            # 4. Chunks oluştur + metadata
            if config.VERBOSE:
                print(f"\n📦 ADIM 4: Chunks Oluşturuluyor...")

            chunks = self.chunker.create_chunks(extraction_results)

            if not chunks:
                return {
                    "status": "error",
                    "error": "Hiç chunk oluşturulamadı"
                }

            # 5. Embeddings + Chromadb
            if config.VERBOSE:
                print(f"\n🔗 ADIM 5: Chromadb'ye Yükleniyor...")

            self.vs.ingest_chunks(chunks)

            # 6. İstatistikler
            divisions = set()
            for chunk in chunks:
                # division STRING'dir, split et!
                division_str = chunk["metadata"]["division"]

                # Virgülle ayrılmış division'ları parse et
                if division_str:
                    for div in division_str.split(","):
                        div_clean = div.strip()
                        if div_clean:  # Boş değerleri skip et
                            divisions.add(div_clean)

            if config.VERBOSE:
                print(f"\n✅ TAMAMLANDI!")
                print(f"   Tümenleri: {list(divisions)}")
                print(f"   Chunks: {len(chunks)}")

            return {
                "status": "success",
                "divisions_found": sorted(list(divisions)),
                "total_paragraphs": len(paragraphs),
                "chunks_created": len(chunks),
                "book_name": self.book_name,
                "book_id": self.book_id
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


def main():
    """Test: PDF yükle ve query et"""

    # Config
    book_name = "Türk İstiklal Harbi - Mondros Mütarekesi"
    book_id = "turk_istiklal_harbi_mondros"

    pipeline = RAGPipeline(book_name, book_id)

    # PDF'leri bul
    pdf_files = list(config.INPUT_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"❌ {config.INPUT_DIR} klasöründe PDF bulunamadı!")
        return

    print(f"\n🎖️  PAGEGENERAL - PDF → LLM → Chromadb\n")
    print(f"📂 {len(pdf_files)} PDF bulundu\n")

    # İlk PDF'i yükle
    pdf_file = pdf_files[0]
    print(f"📥 Yükleniyor: {pdf_file.name}\n")

    ingest_result = pipeline.ingest_pdf(pdf_file)

    if ingest_result['status'] != 'success':
        print(f"\n❌ Hata: {ingest_result['error']}")
        return

    print(f"\n" + "=" * 60)
    print(f"📊 SONUÇLAR:")
    print(f"=" * 60)
    print(f"✅ Tümenleri: {', '.join(ingest_result['divisions_found'])}")
    print(f"📝 Toplam Paragraf: {ingest_result['total_paragraphs']}")
    print(f"📦 Oluşturulan Chunks: {ingest_result['chunks_created']}")
    print(f"=" * 60)


if __name__ == "__main__":
    main()