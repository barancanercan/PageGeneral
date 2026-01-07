#!/usr/bin/env python3
"""
PAGEGENERAL - İnteraktif Sorgu Sistemi
PDF yükle → Chromadb'ye koy → Sorular sor
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
    # Fallback
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
    print("🎖️  PAGEGENERAL - İnteraktif Sorgu Sistemi")
    print("=" * 70)
    print("Tarihsel belgelerden soru sor")
    print("Türk Piyade Tümenlerini arayabilirsin")
    print("'quit', 'exit' veya 'q' yazarak çık")
    print("=" * 70 + "\n")


def print_separator(title=""):
    """Ayırıcı göster"""
    if title:
        print(f"\n{title}")
    print("-" * 70)


def main():
    """Ana program"""

    print_header()

    # Ollama'nın açık olup olmadığını kontrol et
    llm = OllamaClient()
    if not llm.is_available():
        print("❌ HATA: Ollama sunucusu çalışmıyor!")
        print("   Lütfen başka bir terminal'de çalıştırın: ollama serve")
        return

    print(f"✅ Ollama bağlı: {config.OLLAMA_BASE_URL}")
    print(f"📦 Model: {config.LLM_MODEL}\n")

    # RAG pipeline'ı başlat
    book_name = "Türk İstiklal Harbi - Mondros Mütarekesi"
    book_id = "turk_istiklal_harbi_mondros"
    pipeline = RAGPipeline(book_name, book_id)

    # PDF'leri bul
    pdf_files = list(config.INPUT_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"❌ {config.INPUT_DIR} klasöründe PDF bulunamadı!")
        print("   Lütfen PDF'leri bu klasöre ekleyin")
        return

    print(f"📂 {len(pdf_files)} PDF bulundu\n")

    # İlk PDF'i yükle
    pdf_file = pdf_files[0]
    print(f"📥 Yükleniyor: {pdf_file.name}")
    print("   Bu biraz sürebilir (LLM extraction)...")

    ingest_result = pipeline.ingest_pdf(pdf_file)

    if ingest_result['status'] != 'success':
        print(f"\n❌ Hata: {ingest_result['error']}")
        return

    # Bulunanan tümenleri göster
    divisions_found = ingest_result['divisions_found']

    print_separator("📍 BULUNAN TÜMENLERI:")
    for i, div in enumerate(divisions_found, 1):
        print(f"  {i}. {div}")

    print(f"\n📊 İstatistikler:")
    print(f"  - Toplam Paragraf: {ingest_result['total_paragraphs']}")
    print(f"  - Oluşturulan Chunks: {ingest_result['chunks_created']}")

    # Query engine oluştur
    query_engine = QueryEngine()

    print_separator("💬 HAZIR! SORULARINI SOR...")
    print()

    # İnteraktif döngü
    while True:
        try:
            # Tümen seçimi
            print(f"Mevcut Tümenleri: {', '.join([str(i) for i in range(1, len(divisions_found) + 1)])}, 'hepsi'")
            div_choice = input("❓ Tümeni Seç (No veya 'hepsi'): ").strip()

            if not div_choice:
                continue

            # Division seç
            if div_choice.lower() == 'hepsi':
                selected_divisions = divisions_found
            else:
                try:
                    idx = int(div_choice) - 1
                    if 0 <= idx < len(divisions_found):
                        selected_divisions = [divisions_found[idx]]
                    else:
                        print("❌ Geçersiz seçim")
                        continue
                except ValueError:
                    print("❌ Geçersiz giriş")
                    continue

            # Soru al
            question = input("❓ Sorun: ").strip()

            # Kontrol
            if not question:
                continue

            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Hoşça kalın!")
                break

            # Her division'da sor
            for division in selected_divisions:
                print_separator(f"💬 CEVAP ({division}):")

                result = query_engine.generate_answer_with_sources(
                    question, division, top_k=5
                )

                # Cevabı göster
                print(f"\n{result['answer']}\n")

                # Kaynakları göster (Berke formatı)
                print_separator("📍 KAYNAKLAR:")
                for i, src in enumerate(result['sources'], 1):
                    page = src['metadata'].get('source_page', '?')
                    book = src['metadata'].get('book_name', 'Bilinmiyor')
                    confidence = src['metadata'].get('confidence', 0)

                    print(f"\n📄 {i}. {book}, Sayfa {page}")
                    print(f"   Güven: {confidence:.0%}")
                    print(f"   ID: {src['id']}")
                    print(f"   Text: {src['document'][:100]}...")

                # Berke formatında JSON'da göster
                if config.VERBOSE:
                    print(f"\n   Berke Format (JSON):")
                    for src in result['sources']:
                        json_str = json.dumps(src, ensure_ascii=False, indent=4)
                        for line in json_str.split('\n'):
                            print(f"   {line}")

                print()

                # Sonucu kaydet
                output_files = list(config.OUTPUT_DIR.glob("*.json"))
                output_file = config.OUTPUT_DIR / f"query_{len(output_files) + 1}.json"

                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                if config.VERBOSE:
                    print(f"💾 Kaydedildi: {output_file}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Çıkılıyor...")
            break
        except Exception as e:
            print(f"❌ Hata: {e}\n")


if __name__ == "__main__":
    main()