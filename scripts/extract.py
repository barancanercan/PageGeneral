#!/usr/bin/env python3
"""
PageGeneral - PDF Extraction Script

Main entry point:
  python scripts/extract.py

Input:  data/input/*.pdf
Output: output/extractions_YYYYMMDD_HHMMSS.json

Format:
  [{
    "para_id": 5,
    "text": "...",
    "divisions": ["4. Piyade Tümeni"],
    "confidence": 0.95,
    "source_page": 1,
    "book_name": "Türk İstiklal Harbi - Mondros Mütarekesi",
    "book_id": "turk_istiklal_harbi_mondros"
  }, ...]
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag_pipeline import RAGPipeline
import config


def main():
    """Main extraction pipeline"""

    print("\n" + "=" * 70)
    print("🎖️  PAGEGENERAL - PDF Division Extraction")
    print("=" * 70)

    # Find PDF files
    pdf_files = list(config.INPUT_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"\n❌ No PDF found in: {config.INPUT_DIR}")
        print("\nHow to use:")
        print("  1. Copy PDF to data/input/")
        print("  2. Run: python scripts/extract.py")
        return 1

    if len(pdf_files) > 1:
        print(f"\n⚠️  Found {len(pdf_files)} PDFs, processing first one")

    pdf_file = pdf_files[0]
    print(f"\n📥 PDF: {pdf_file.name}\n")

    # Setup pipeline
    book_name = "Türk İstiklal Harbi - Mondros Mütarekesi"
    book_id = "turk_istiklal_harbi_mondros"

    pipeline = RAGPipeline(book_name, book_id)

    # Extract
    try:
        print("🚀 Starting extraction...\n")
        results = pipeline.extract_divisions(pdf_file)

        # Save output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = config.OUTPUT_DIR / f"extractions_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        # Statistics
        divisions_found = set()
        for result in results:
            for div in result["divisions"]:
                divisions_found.add(div)

        print("\n" + "=" * 70)
        print("✅ EXTRACTION COMPLETE!")
        print("=" * 70)
        print(f"Total results: {len(results)}")
        print(f"Divisions found: {len(divisions_found)}")
        for div in sorted(divisions_found):
            count = sum(1 for r in results if div in r["divisions"])
            print(f"  - {div}: {count}")

        print(f"\n📁 Output: {output_file}")
        print("=" * 70 + "\n")

        # Show first sample
        if results:
            print("📊 Sample record:")
            print(json.dumps(results[0], ensure_ascii=False, indent=2))
            print()

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Extraction stopped by user")
        return 1

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())