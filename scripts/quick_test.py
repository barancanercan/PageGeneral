#!/usr/bin/env python3
"""
PAGEGENERAL - Quick Test (Sadece 100 paragraf)
Hızlı test için ilk 100 paragrafa sınırla
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.rag_pipeline import RAGPipeline
    from src.query_engine import QueryEngine
    from src.llm import OllamaClient
    import config
except ImportError:
    sys.path.insert(0, str(project_root / "src"))
    from rag_pipeline import RAGPipeline
    from query_engine import QueryEngine
    from llm import OllamaClient
    sys.path.insert(0, str(project_root))
    import config

import json


def print_header():
    """Başlık göster"""
    print("\n" + "=" * 70)
    print("🎖️  PAGEGENERAL - QUICK TEST (100 Paragraf)")
    print("=" * 70)
    print("Hızlı test için ilk 100 paragraf")
    print("=" * 70 + "\n")


def print_separator(title=""):
    """Ayırıcı göster"""
    if title:
        print(f"\n{title}")
    print("-" * 70)


def main():
    """Ana test"""

    print_header()

    # Ollama kontrol
    llm = OllamaClient()
    if not llm.is_available():
        print("❌ Ollama açık değil!")
        return

    print(f"✅ Ollama bağlı: {config.OLLAMA_BASE_URL}\n")

    # RAG pipeline
    book_name = "Türk İstiklal Harbi - Mondros Mütarekesi (TEST)"
    book_id = "turk_istiklal_harbi_mondros_test"
    pipeline = RAGPipeline(book_name, book_id)

    # PDF bul
    pdf_files = list(config.INPUT_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ PDF bulunamadı!")
        return

    pdf_file = pdf_files[0]
    print(f"📥 Yükleniyor: {pdf_file.name}")

    # Parse PDF
    parse_result = pipeline.parser.parse(pdf_file)
    if parse_result['status'] != 'success':
        print(f"❌ Parse hatası: {parse_result['error']}")
        return

    content = parse_result['content']

    # Paragraf böl
    paragraphs = content.split('\n\n')
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    # ⚠️ İLK 100 PARAGRAFI AL
    paragraphs_test = paragraphs[:100]

    print(f"✂️  {len(paragraphs_test)} paragraf işlenecek (100 limit)\n")

    # LLM extraction
    print(f"🤖 Division Extraction (100 para)...\n")
    extraction_results = pipeline.extractor.extract(paragraphs_test, verbose=True)

    # Chunks
    print(f"\n📦 Chunks oluşturuluyor...")
    chunks = pipeline.chunker.create_chunks(extraction_results)
    print(f"✂️  {len(chunks)} chunk oluşturuldu")

    if not chunks:
        print("❌ Hiç chunk yok!")
        return

    # Chromadb ingestion
    print(f"\n🔗 Chromadb'ye yükleniyor...")
    pipeline.vs.ingest_chunks(chunks)

    # İstatistikler
    divisions = set()
    for chunk in chunks:
        division_str = chunk["metadata"]["division"]
        if division_str:
            for div in division_str.split(","):
                div_clean = div.strip()
                if div_clean:
                    divisions.add(div_clean)

    print_separator("📍 BULUNAN TÜMENLERI:")
    for i, div in enumerate(sorted(divisions), 1):
        print(f"  {i}. {div}")

    print(f"\n📊 İstatistikler:")
    print(f"  - Test Paragraf: {len(paragraphs_test)}")
    print(f"  - Chunks: {len(chunks)}")
    print(f"  - Divisions: {len(divisions)}")

    # Query Engine test
    query_engine = QueryEngine()

    print_separator("💬 QUERY TEST...")

    test_questions = [
        ("4. Piyade Tümeni", "Bu tümen nerede savaştı?"),
        ("9. Piyade Tümeni", "Tümenin komutanı kimdi?"),
    ]

    for division, question in test_questions:
        if division not in divisions:
            print(f"\n⚠️  {division} bulunamadı, skip...")
            continue

        print(f"\n❓ Sorgu: {question}")
        print(f"📍 Division: {division}")

        result = query_engine.generate_answer_with_sources(question, division, top_k=3)

        print(f"\n💬 Cevap:\n{result['answer']}\n")

        print(f"📍 Kaynaklar ({len(result['sources'])}):")
        for src in result['sources']:
            page = src['metadata'].get('source_page')
            print(f"  - {src['id']}: s.{page}")

    print_separator()
    print("✅ QUICK TEST TAMAMLANDI!\n")


if __name__ == "__main__":
    main()
