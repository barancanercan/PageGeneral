#!/usr/bin/env python3
"""
PAGEGENERAL - İnteraktif Sorgu Sistemi
Kullanıcıdan soru al → RAG pipeline → Cevap göster
"""

import sys
from pathlib import Path

# src klasörünü path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_pipeline import RAGPipeline
from src.llm import OllamaClient
import config
import json


def print_header():
    """Başlık göster"""
    print("\n" + "=" * 60)
    print("🎖️  PAGEGENERAL - İnteraktif Sorgu Sistemi")
    print("=" * 60)
    print("Tarihsel belgelerden soru sor")
    print("'quit' veya 'exit' yazarak çık")
    print("=" * 60 + "\n")


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
    pipeline = RAGPipeline()

    # PDF'leri yükle
    pdf_files = list(config.INPUT_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"❌ {config.INPUT_DIR} klasöründe PDF bulunamadı!")
        return

    print(f"📂 {len(pdf_files)} PDF bulundu\n")

    # İlk PDF'i yükle
    pdf_file = pdf_files[0]
    print(f"📥 Yükleniyor: {pdf_file.name}")

    ingest_result = pipeline.ingest_pdf(pdf_file)

    if ingest_result['status'] != 'success':
        print(f"❌ Hata: {ingest_result['error']}")
        return

    content = ingest_result['content']
    chunks = ingest_result['chunks']

    print(f"✅ {len(chunks)} chunk oluşturuldu\n")
    print("-" * 60)
    print("💡 Hazır! Sorularını sor...\n")

    # İnteraktif döngü
    while True:
        try:
            # Soru al
            question = input("❓ Sorun: ").strip()

            # Kontrol
            if not question:
                continue

            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Hoşça kalın!")
                break

            # Sorguyu çalıştır
            query_result = pipeline.query(question, content)

            if query_result['status'] == 'success':
                # Cevabı göster
                print(f"\n💬 Cevap:")
                print("-" * 60)
                print(query_result['answer'])
                print("-" * 60)

                # Güven puanı
                confidence = query_result.get('confidence', 0)
                print(f"📊 Güven: {confidence:.0%}\n")

                # JSON'a kaydet
                pipeline.save_result(query_result)

            else:
                print(f"❌ {query_result.get('error', 'Bilinmeyen hata')}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Çıkılıyor...")
            break
        except Exception as e:
            print(f"❌ Hata: {e}\n")


if __name__ == "__main__":
    main()