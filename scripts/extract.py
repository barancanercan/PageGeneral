#!/usr/bin/env python3
"""
PAGEGENERAL - Division Extraction Script
Turkish Military Division extraction from historical PDFs
Using HuggingFace Qwen2.5-7B-Instruct + LLM-based extraction
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import datetime
from src.pdf_parser import PDFParser
from src.division_extractor import DivisionExtractor
import config


def main():
    print("\n" + "=" * 80)
    print("🎖️  PAGEGENERAL - Division Extraction")
    print("=" * 80)
    
    pdf_files = list(config.INPUT_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ {config.INPUT_DIR} klasöründe PDF bulunamadı!")
        return
    
    print(f"\n📂 {len(pdf_files)} PDF bulundu\n")
    
    divisions = config.DIVISION_LIST
    print(f"📋 {len(divisions)} tümen target:")
    for div in divisions:
        print(f"   - {div}")
    
    all_results = []
    
    for pdf_file in pdf_files:
        print(f"\n📥 Yükleniyor: {pdf_file.name}")
        
        parser = PDFParser()
        parse_result = parser.parse(pdf_file)
        
        if parse_result['status'] != 'success':
            print(f"❌ Parse hatası: {parse_result.get('error')}")
            continue
        
        content = parse_result['content']
        
        paragraphs = content.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        print(f"✂️  {len(paragraphs)} paragraf oluşturuldu")
        
        print(f"\n🔍 Extraction başlıyor...")
        extractor = DivisionExtractor(divisions)
        results = extractor.extract(paragraphs, verbose=True)
        
        for result in results:
            result['book'] = pdf_file.stem
            result['timestamp'] = datetime.now().isoformat()
        
        all_results.extend(results)
        
        print(f"\n✅ {len(results)} paragraf işlendi")
    
    if all_results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = config.OUTPUT_DIR / f"extractions_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Kaydedildi: {output_file}")
        print(f"   ({len(all_results)} extraction)")
        
        print("\n📊 SUMMARY:")
        print("=" * 80)
        
        unique_divisions = set()
        for result in all_results:
            unique_divisions.update(result.get('divisions', []))
        
        print(f"✅ Toplam extraction: {len(all_results)}")
        print(f"✅ Benzersiz tümen: {len(unique_divisions)}")
        print(f"✅ Çıktı: {output_file}")
        
        if unique_divisions:
            print(f"\n🎖️  Bulunmuş tümenleri:")
            for div in sorted(unique_divisions):
                count = sum(1 for r in all_results if div in r.get('divisions', []))
                print(f"   - {div}: {count} paragraf")
    else:
        print("\n⚠️  Hiç extraction bulunamadı")
    
    print("\n" + "=" * 80)
    print("✅ İşlem tamamlandı!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
