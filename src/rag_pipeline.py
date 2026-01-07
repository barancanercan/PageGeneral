"""
PageGeneral - RAG Pipeline
Simplified: PDF → Extract divisions → JSON
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pdf_parser import PDFParser
from src.division_extractor import DivisionExtractor
import config


class RAGPipeline:
    """Extract Turkish Infantry Divisions from PDF"""

    def __init__(self, book_name: str, book_id: str):
        self.book_name = book_name
        self.book_id = book_id
        self.parser = PDFParser()
        self.extractor = DivisionExtractor(config.DIVISION_LIST)

    def extract_divisions(self, pdf_path):
        """
        Main pipeline: PDF → Extract divisions → JSON output

        Args:
            pdf_path: Path to PDF file

        Returns:
            List[{
                "para_id": int,
                "text": str,
                "divisions": [str],
                "confidence": float,
                "source_page": int,
                "book_name": str,
                "book_id": str
            }]
        """

        if config.VERBOSE:
            print(f"\n📄 STEP 1: PDF Parse")

        # 1. Parse PDF → Text
        parse_result = self.parser.parse(pdf_path)

        if parse_result['status'] != 'success':
            raise Exception(f"PDF parse failed: {parse_result['error']}")

        content = parse_result['content']

        if config.VERBOSE:
            print(f"\n✂️  STEP 2: Split Paragraphs")

        # 2. Split paragraphs
        paragraphs = content.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        if config.VERBOSE:
            print(f"   {len(paragraphs)} paragraphs found")

        if config.VERBOSE:
            print(f"\n🤖 STEP 3: LLM Division Extraction")

        # 3. Extract divisions (LLM)
        extraction_results = self.extractor.extract(paragraphs, verbose=True)

        if config.VERBOSE:
            print(f"\n📦 STEP 4: Format Output")

        # 4. Format output (Berke format)
        output = []

        for result in extraction_results:
            # Skip if no divisions found
            if not result["divisions"]:
                continue

            # Create output record
            record = {
                "para_id": result["para_id"],
                "text": result["text"],
                "divisions": result["divisions"],
                "confidence": result["confidence"],
                "source_page": self._calculate_page(result["para_id"]),
                "book_name": self.book_name,
                "book_id": self.book_id
            }

            output.append(record)

        if config.VERBOSE:
            print(f"   {len(output)} records with divisions")

        return output

    def _calculate_page(self, para_id: int) -> int:
        """
        Estimate page number from paragraph ID

        Assumption: ~50 paragraphs per page
        """
        return (para_id // 50) + 1