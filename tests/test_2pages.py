#!/usr/bin/env python3
"""
Test: Tümen geçen sayfaları tara ve çıktı formatını kontrol et
Sayfa aralığı: 240-245 (tümen geçen sayfalar)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from src.pdf_parser import PDFParser
from src.division_extractor import DivisionExtractor
import config


def main():
    print("\n" + "=" * 70)
    print("TEST: Sayfa 240-245 Extraction (Tümen içeren sayfalar)")
    print("=" * 70)

    # PDF bul
    pdf_files = list(config.INPUT_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"PDF bulunamadı: {config.INPUT_DIR}")
        return

    pdf_file = pdf_files[0]
    print(f"\nPDF: {pdf_file.name}")

    # Parse et
    parser = PDFParser()
    result = parser.parse(pdf_file)

    if result['status'] != 'success':
        print(f"Parse hatası: {result.get('error')}")
        return

    # Sayfa 240-245 arasındaki paragrafları al (tümen geçen sayfalar)
    all_paragraphs = result.get('paragraphs', [])
    test_paragraphs = [p for p in all_paragraphs if 240 <= p['page'] <= 245]

    print(f"\nToplam paragraf: {len(all_paragraphs)}")
    print(f"Sayfa 240-245 paragraf: {len(test_paragraphs)}")

    # Extraction
    print(f"\nExtraction başlıyor...")
    extractor = DivisionExtractor(config.DIVISION_LIST)
    results = extractor.extract(test_paragraphs, verbose=True)

    # Sonuçları göster
    print("\n" + "=" * 70)
    print("SONUÇLAR:")
    print("=" * 70)

    for r in results:
        print(f"\n[Sayfa {r['metadata']['source_page']}] {r['id']}")
        print(f"  Metin: {r['document'][:100]}...")
        print(f"  Tümenler: {r['metadata']['division']}")
        print(f"  Güven: {r['metadata']['confidence']:.0%}")

    # JSON kaydet
    output_file = config.OUTPUT_DIR / "test_2pages_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nKaydedildi: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
