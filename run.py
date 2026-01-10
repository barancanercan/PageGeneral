#!/usr/bin/env python3
"""
PageGeneral - CLI

Kullanım:
  python run.py ingest              # PDF'leri VectorDB'ye yükle
  python run.py query -s            # Tümen özeti
  python run.py query -d            # Sadece tümen içeren paragrafları export et
"""

# PyTorch DLL fix
try:
    import torch
except ImportError:
    pass

import argparse
from pathlib import Path


def cmd_ingest(args):
    """PDF → VectorDB"""
    from src.ingest import IngestPipeline

    pipeline = IngestPipeline()

    if args.path:
        path = Path(args.path)
        if path.is_file():
            result = pipeline.ingest_pdf(path, force=args.force)
        else:
            result = pipeline.ingest_folder(path, force=args.force)
    else:
        result = pipeline.ingest_folder(force=args.force)

    if result["status"] == "success":
        count = result.get('processed', result.get('paragraphs', 0))
        print(f"\n[OK] VectorDB'ye yuklendi: {count}")
    elif result["status"] == "skipped":
        print(f"\n[SKIP] Zaten yuklu")
    else:
        print(f"\n[ERROR] {result.get('message')}")


def cmd_query(args):
    """VectorDB → JSON"""
    from src.query import DivisionQuery

    query = DivisionQuery()

    if args.list:
        books = query.list_books()
        print("\nYuklu Kitaplar:")
        for b in books:
            print(f"  - {b['title']} ({b['paragraphs']} paragraf)")
        return

    if args.summary:
        summary = query.get_divisions_summary(args.book)
        print(f"\nOzet:")
        print(f"  Paragraf: {summary['total_paragraphs']}")
        print(f"  Tumen iceren: {summary['paragraphs_with_divisions']}")
        print(f"  Tumenler: {summary['divisions']}")
        return

    # Export
    result = query.export_json(
        book_id=args.book,
        only_with_divisions=args.divisions_only,
        include_embeddings=True
    )

    print(f"\n[OK] Export: {result['output_file']}")
    print(f"  Paragraf: {result['total_paragraphs']}")
    print(f"  Tumenler: {result['divisions_found']}")


def main():
    parser = argparse.ArgumentParser(description="PageGeneral CLI")
    subparsers = parser.add_subparsers(dest="command")

    # ingest
    p1 = subparsers.add_parser("ingest", help="PDF → VectorDB")
    p1.add_argument("path", nargs="?", help="PDF/klasör")
    p1.add_argument("-f", "--force", action="store_true")

    # query
    p2 = subparsers.add_parser("query", help="VectorDB → JSON")
    p2.add_argument("-b", "--book", help="Kitap ID")
    p2.add_argument("-d", "--divisions-only", action="store_true")
    p2.add_argument("-s", "--summary", action="store_true")
    p2.add_argument("-l", "--list", action="store_true")
    p2.add_argument("-o", "--output", help="Çıktı dosyası")

    args = parser.parse_args()

    if args.command == "ingest":
        cmd_ingest(args)
    elif args.command == "query":
        cmd_query(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
