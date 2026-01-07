"""
PAGEGENERAL - Query Engine (Core)
Query sor → Berke formatında döndür + Answer ile birlikte
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.vector_store import VectorStore
    from src.llm import OllamaClient
    import config
except ImportError:
    # Fallback
    sys.path.insert(0, str(project_root / "src"))
    from vector_store import VectorStore
    from llm import OllamaClient
    sys.path.insert(0, str(project_root))
    import config

from typing import List, Dict
from datetime import datetime


class QueryEngine:
    """Query sor → Berke formatında dokümanlı cevap döndür"""

    def __init__(self):
        self.vs = VectorStore()
        self.llm = OllamaClient()

    def query(self, question: str, division: str, top_k: int = 5) -> List[Dict]:
        """
        Query → Chromadb search → Berke formatında sonuç
        """
        if config.VERBOSE:
            print(f"\n🔍 Searching division: {division}")

        # Vector search
        search_results = self.vs.search(question, division, top_k)

        # Format Berke'ye
        formatted_results = self.vs.format_results_berke(search_results)

        if config.VERBOSE:
            print(f"   ✓ {len(formatted_results)} result found")

        return formatted_results

    def generate_answer_with_sources(self, question: str, division: str, top_k: int = 5) -> Dict:
        """Answer + Sources (full response)"""

        # 1. Search
        search_results = self.query(question, division, top_k)

        # 2. Context oluştur
        context_parts = []
        for r in search_results:
            page = r["metadata"].get("source_page", "?")
            book = r["metadata"].get("book_name", "Bilinmiyor")
            text = r["document"]
            context_parts.append(f"[{book}, s.{page}]\n{text}")

        context = "\n\n---\n\n".join(context_parts)

        # 3. LLM'den cevap al
        prompt = f"""Verilen bağlamdan hareketle soruyu cevaplayınız.

TÜMEN: {division}

BAĞLAM:
{context}

SORU:
{question}

Cevap (Türkçe, sadece bağlamdan, kısa ve açık):"""

        if config.VERBOSE:
            print(f"🤖 Generating answer...")

        answer = self.llm.generate(prompt)

        return {
            "question": question,
            "division": division,
            "answer": answer,
            "sources": search_results,
            "timestamp": datetime.now().isoformat()
        }


def test_query_engine():
    """Test: query engine çalışıyor mu?"""
    print("🧪 Query Engine Test\n")

    engine = QueryEngine()

    if not engine.llm.is_available():
        print("❌ Ollama açık değil!")
        return

    print("✅ Ollama açık\n")

    question = "Tümen nerede savaştı?"
    division = "4. Piyade Tümeni"

    print(f"❓ Sorgu: {question}")
    print(f"📍 Division: {division}\n")

    results = engine.query(question, division, top_k=3)
    print(f"📊 {len(results)} sonuç bulundu\n")

    if results:
        for i, r in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"  ID: {r['id']}")
            print(f"  Page: {r['metadata'].get('source_page')}")
            print(f"  Confidence: {r['metadata'].get('confidence', 0):.0%}")
            print()

    print("=" * 60)
    print("💬 ANSWER + SOURCES:")
    print("=" * 60)

    result_with_answer = engine.generate_answer_with_sources(question, division)
    print(f"\nQuestion: {result_with_answer['question']}")
    print(f"Division: {result_with_answer['division']}")
    print(f"\nAnswer:\n{result_with_answer['answer']}")
    print(f"\nSources ({len(result_with_answer['sources'])}):")

    for src in result_with_answer['sources']:
        print(f"  - {src['id']}: {src['document'][:60]}...")

    print("\n✅ Test tamamlandı")


if __name__ == "__main__":
    test_query_engine()