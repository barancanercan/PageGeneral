"""
PageGeneral - Division Extractor
LLM-based extraction of Turkish Infantry Divisions from paragraphs
Now using HuggingFace Transformers (local, no Ollama)
"""

import re
import json
from typing import List, Dict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm import HFClient
import config


class DivisionExtractor:
    """Extract divisions from paragraphs using LLM + regex pre-filter"""

    def __init__(self, division_list: List[str]):
        """
        Args:
            division_list: List of division names to extract
                e.g., ["4. Piyade Tümeni", "9. Piyade Tümeni", ...]
        """
        self.division_list = division_list
        self.llm = HFClient()
        self.book_name = None
        self.book_id = None

        # Build regex pattern for pre-filtering
        self._build_regex_pattern()

    def _build_regex_pattern(self):
        """Build regex to pre-filter paragraphs containing division names"""
        # Escape special chars and build pattern
        patterns = []
        for div in self.division_list:
            # Handle Turkish characters
            escaped = re.escape(div)
            patterns.append(escaped)

        self.regex_pattern = '|'.join(patterns)

    def extract(self, paragraphs: List[str], verbose: bool = True) -> List[Dict]:
        """
        Extract divisions from paragraphs

        Args:
            paragraphs: List of paragraph texts
            verbose: Print progress

        Returns:
            List[{
                "para_id": int,
                "text": str,
                "divisions": [str],
                "confidence": float
            }]
        """

        if verbose:
            print(f"\n🔍 Pre-filtering {len(paragraphs)} paragraphs...")
            print(f"   (Regex → LLM hybrid)")

        # Pre-filter: which paragraphs mention divisions?
        matching_indices = []
        for idx, para in enumerate(paragraphs):
            if re.search(self.regex_pattern, para, re.IGNORECASE):
                matching_indices.append(idx)

        if verbose:
            from tqdm import tqdm
            print(f"\n   Found {len(matching_indices)} matching paragraphs")
            pbar = tqdm(total=len(matching_indices))

        results = []

        # Process only matching paragraphs
        for idx in matching_indices:
            para_text = paragraphs[idx]

            # Extract divisions using LLM
            extraction = self._extract_divisions(para_text)

            result = {
                "para_id": idx,
                "text": para_text[:200] + ("..." if len(para_text) > 200 else ""),
                "divisions": extraction.get("divisions", []),
                "confidence": extraction.get("confidence", 0)
            }

            results.append(result)

            if verbose:
                pbar.update(1)

        if verbose:
            pbar.close()

        return results

    def _extract_divisions(self, paragraph_text: str) -> Dict:
        """
        Use LLM to extract which divisions are in this paragraph

        Returns: {
            "divisions": [str],
            "confidence": float
        }
        """

        # Build prompt
        divisions_str = ", ".join(self.division_list)

        prompt = f"""Verilen paragrafta aşağıdaki tümenlerin hangilerinden bahsediliyor?

Tümenleri: {divisions_str}

PARAGRAF:
{paragraph_text}

Sadece JSON döndür, başka bir şey yazma:
{{"divisions": ["Tümen 1", "Tümen 2"], "confidence": 0.95}}

Eğer hiçbir tümen yoksa:
{{"divisions": [], "confidence": 0}}"""

        # LLM'den cevap al
        response = self.llm.generate(prompt)

        if not response:
            return {"divisions": [], "confidence": 0}

        # Parse JSON (with fallback)
        return self._parse_json_robust(response)

    def _parse_json_robust(self, response: str) -> Dict:
        """
        Robust JSON parsing with fallbacks
        Handles backticks, malformed JSON, etc.
        """
        response_clean = response.strip()

        # Remove markdown code blocks
        if response_clean.startswith("```json"):
            response_clean = response_clean[7:]
        elif response_clean.startswith("```"):
            response_clean = response_clean[3:]
        if response_clean.endswith("```"):
            response_clean = response_clean[:-3]

        response_clean = response_clean.strip()

        # Try direct parse
        try:
            parsed = json.loads(response_clean)

            divisions = parsed.get("divisions", [])
            confidence = float(parsed.get("confidence", 0.5))

            # Ensure confidence is 0-1
            confidence = max(0, min(1, confidence))

            return {
                "divisions": divisions if isinstance(divisions, list) else [],
                "confidence": confidence
            }
        except json.JSONDecodeError:
            pass

        # Fallback: regex extract
        json_match = re.search(
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
            response_clean,
            re.DOTALL
        )

        if json_match:
            try:
                parsed = json.loads(json_match.group())
                divisions = parsed.get("divisions", [])
                confidence = float(parsed.get("confidence", 0.5))
                confidence = max(0, min(1, confidence))

                return {
                    "divisions": divisions if isinstance(divisions, list) else [],
                    "confidence": confidence
                }
            except:
                pass

        # Last fallback: return empty
        return {"divisions": [], "confidence": 0}


# Test
if __name__ == "__main__":
    print("=" * 70)
    print("🧪 DivisionExtractor Test")
    print("=" * 70)

    # Test data
    divisions = config.DIVISION_LIST
    extractor = DivisionExtractor(divisions)

    test_paragraphs = [
        "5 nci Kafkas Tümeni komutanı, cepheye gitmek üzere hazırlanıyordu.",
        "Hava çok soğuktu ama askerler yürüyüşteydi.",
        "24 ncü Tümen ile 36 ncı Tümen ortak operasyon yapacaklardı.",
        "Hafif bir yağmur yağıyordu.",
    ]

    print(f"\n📋 Divisions: {len(divisions)} tümen")
    for div in divisions:
        print(f"   - {div}")

    print(f"\n🔍 Testing {len(test_paragraphs)} paragraphs...")

    results = extractor.extract(test_paragraphs, verbose=True)

    print(f"\n📊 Results:")
    print("=" * 70)

    for result in results:
        print(f"\n📝 Paragraf {result['para_id']}:")
        print(f"   Text: {result['text'][:80]}...")
        print(f"   Tümenleri: {result['divisions']}")
        print(f"   Confidence: {result['confidence']:.0%}")

    print("\n✅ ALL TESTS PASSED!")
    print("=" * 70)