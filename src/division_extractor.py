"""
PAGEGENERAL - Division Extraction Agent
Paragraf paragraf oku → LLM ile extraction → Hangi tümenleri içeriyor?
"""

import json
from src.llm import OllamaClient
import config
from tqdm import tqdm


class DivisionExtractor:
    """LLM-based: Her paragraftan divisions çıkar"""

    def __init__(self, division_list=None):
        self.llm = OllamaClient()
        self.divisions = division_list or config.DIVISION_LIST

    def extract(self, paragraphs, verbose=True):
        """
        Smart extraction: Regex → LLM
        Önce regex ile tümen adlarını ara (hızlı)
        Sonra LLM'ye gönder (sadece matching)
        """
        import re

        results = []
        llm_calls = 0

        # Regex patterns (division nombres)
        patterns = [
            r'\b4\.?\s+(?:Piyade\s+)?Tümen',
            r'\b5\.?\s+(?:Piyade\s+)?Tümen',
            r'\b7\.?\s+(?:Piyade\s+)?Tümen',
            r'\b9\.?\s+(?:Piyade\s+)?Tümen',
            r'\b23\.?\s+(?:Piyade\s+)?Tümen',
            r'\b24\.?\s+(?:Piyade\s+)?Tümen',
            r'Tümen\b',  # Generic
        ]

        combined_pattern = '|'.join(f'({p})' for p in patterns)

        if verbose:
            print(f"\n🔍 Pre-filtering {len(paragraphs)} paragraf...")
            print(f"   (Regex → LLM hybrid)\n")

        iterator = tqdm(enumerate(paragraphs)) if verbose else enumerate(paragraphs)

        for para_id, para_text in iterator:
            # Boş paragraf skip
            if not para_text.strip() or len(para_text.strip()) < 20:
                continue

            # ADIM 1: Regex pre-check (çok hızlı!)
            has_division_keyword = re.search(combined_pattern, para_text, re.IGNORECASE)

            if not has_division_keyword:
                # Tümen adı yok → LLM'ye gitme, boş sonuç dön
                results.append({
                    "para_id": para_id,
                    "text": para_text.strip(),
                    "divisions": [],
                    "confidence": 0
                })
                continue

            # ADIM 2: Sadece matching paragraflar LLM'ye git
            extraction = self._extract_divisions(para_text)
            llm_calls += 1

            results.append({
                "para_id": para_id,
                "text": para_text.strip(),
                "divisions": extraction["divisions"],
                "confidence": extraction["confidence"]
            })

        if verbose:
            print(f"\n✅ {len(results)} paragraftan extraction yapıldı")
            print(f"   (LLM calls: {llm_calls}/{len(paragraphs)} = %{llm_calls * 100 // len(paragraphs)})\n")

        return results

    def _extract_divisions(self, para_text):
        """
        Tek paragraftan divisions çıkar

        Returns:
            {
                "divisions": ["4. Piyade Tümeni", "9. Piyade Tümeni"],
                "confidence": 0.95
            }
        """

        # Divisions formatını hazırla
        divisions_formatted = "\n".join([f"- {d}" for d in self.divisions])

        prompt = f"""GÖREV: Verilen paragrafta aşağıdaki Türk Piyade Tümenlerinin hangilerinden bahsediliyor?

        MÜMKÜN TÜMENLERI (FULL LİST):
        {divisions_formatted}

        PARAGRAF:
        {para_text}

        TALIMATLAR:
        1. Paragrafı DİKKATLİ OKU
        2. Tüm tümen adlarını ara
        3. EXAM BU TÜMENLERIN ADLARINI:
           - "4. Piyade Tümeni" (veya "Dördüncü Piyade Tümeni")
           - "5. Piyade Tümeni" (veya "Beşinci Piyade Tümeni")
           - "23. Piyade Tümeni" (veya "Yirmiüçüncü Piyade Tümeni")
           - "24. Piyade Tümeni" (veya "Yirmidördüncü Piyade Tümeni")
           - "7. Piyade Tümeni" (veya "Yedinci Piyade Tümeni")
           - "9. Piyade Tümeni" (veya "Dokuzuncu Piyade Tümeni")

        4. Eğer sadece numara varsa (ör: "9. Tümen") bunu match et
        5. Eğer alternatif isim varsa (ör: "Dokuzuncu Tümen") bunu match et

        SADECE BU JSON FORMATINDA CEVAP VER (başka hiçbir şey yok):
        {{"divisions": ["4. Piyade Tümeni", "9. Piyade Tümeni"], "confidence": 0.95}}

        Eğer hiç tümen yoksa:
        {{"divisions": [], "confidence": 0}}

        JSON:"""

        try:
            response = self.llm.generate(prompt)

            if not response:
                return {"divisions": [], "confidence": 0}

            # JSON parse et
            try:
                # Geçersiz karakterleri temizle
                response_clean = response.strip()
                if response_clean.startswith("```json"):
                    response_clean = response_clean.replace("```json", "").replace("```", "").strip()
                elif response_clean.startswith("```"):
                    response_clean = response_clean.replace("```", "").strip()

                parsed = json.loads(response_clean)
                return {
                    "divisions": parsed.get("divisions", []),
                    "confidence": min(max(parsed.get("confidence", 0.5), 0), 1.0)
                }

            except json.JSONDecodeError:
                if config.VERBOSE:
                    print(f"⚠️  JSON parse hatası: {response[:100]}")
                return {"divisions": [], "confidence": 0}

        except Exception as e:
            if config.VERBOSE:
                print(f"❌ Extraction hatası: {e}")
            return {"divisions": [], "confidence": 0}


def test_extractor():
    """Test: extraction çalışıyor mu?"""

    print("🧪 Division Extractor Test\n")

    # Test paragrafları
    test_paragraphs = [
        "4. Piyade Tümeni komutanı, cepheye gitmek üzere hazırlanıyordu.",
        "Hava çok soğuktu ama askerler yürüyüşteydi.",
        "9. Piyade Tümeni ile 24. Piyade Tümeni ortak operasyon yapacaklardı.",
        "Hafif bir yağmur yağıyordu."
    ]

    extractor = DivisionExtractor()

    print(f"📋 Tümen Listesi: {len(extractor.divisions)} tümen")
    for div in extractor.divisions:
        print(f"   - {div}")

    print(f"\n🔍 {len(test_paragraphs)} test paragrafu işleniyor...\n")

    results = extractor.extract(test_paragraphs, verbose=True)

    print("\n📊 Sonuçlar:")
    print("=" * 60)

    for result in results:
        print(f"\n📝 Paragraf {result['para_id']}:")
        print(f"   Text: {result['text'][:80]}...")
        print(f"   Tümenleri: {result['divisions']}")
        print(f"   Confidence: {result['confidence']:.0%}")

    print("\n✅ Test tamamlandı")


if __name__ == "__main__":
    test_extractor()