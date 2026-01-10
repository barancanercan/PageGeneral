"""
PAGEGENERAL - PDF Parser (Hafif Versiyon)
pypdf ile basit metin çıkarma + Division detection
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple
from pypdf import PdfReader
import config


def get_compiled_patterns():
    """Config'den pattern'leri al ve compile et"""
    return [re.compile(p, re.IGNORECASE) for p in config.DIVISION_PATTERNS]


def detect_divisions(text: str) -> Tuple[List[str], float]:
    """
    Metinde tümen/division referanslarını tespit et.

    Returns:
        (divisions_list, confidence_score)
    """
    divisions = set()
    patterns = get_compiled_patterns()

    for pattern in patterns:
        matches = pattern.findall(text)
        for match in matches:
            # Sadece sayıyı al ve normalize et
            div_num = str(match).strip()
            if div_num.isdigit():
                divisions.add(div_num)

    # Confidence: bulunan division sayısına göre
    if not divisions:
        return [], 0.0
    elif len(divisions) == 1:
        return list(divisions), 0.95
    elif len(divisions) <= 3:
        return list(divisions), 0.85
    else:
        return list(divisions), 0.75


class PDFParser:
    """PDF → Markdown dönüştürücü (Hafif)"""

    def parse(self, pdf_path: str | Path) -> dict:
        """
        PDF'i parse et (basit text extraction)

        Args:
            pdf_path: PDF dosyasının yolu

        Returns:
            {
                "status": "success" | "error",
                "content": markdown metni,
                "output_path": kaydedildiği yer,
                "pages": sayfa sayısı,
                "error": hata mesajı (varsa)
            }
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            return {"status": "error", "error": f"Dosya bulunamadı: {pdf_path}"}

        try:
            if config.VERBOSE:
                print(f"[PARSE] {pdf_path.name}")

            # pypdf ile oku
            reader = PdfReader(str(pdf_path))
            num_pages = len(reader.pages)

            markdown_content = f"# {pdf_path.stem}\n\n"
            markdown_content += f"**Kaynak:** {pdf_path.name}\n"
            markdown_content += f"**Sayfalar:** {num_pages}\n\n"
            markdown_content += "---\n\n"

            # Her sayfadan metin çıkar
            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text()

                # Boşlukları temizle
                text = text.strip()

                if text:
                    markdown_content += f"## Sayfa {i}\n\n{text}\n\n---\n\n"

            # Markdown'ı kaydet
            output_file = config.PROCESSED_DIR / f"{pdf_path.stem}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            if config.VERBOSE:
                print(f"[OK] Kaydedildi: {output_file}")

            # Sayfa bazlı paragrafları çıkar + division detection
            paragraphs_with_pages = []
            all_divisions = set()  # Tüm doküman için

            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text and text.strip():
                    # Her sayfadaki paragrafları ayır
                    page_paragraphs = text.strip().split('\n\n')
                    for para in page_paragraphs:
                        para = para.strip()
                        if para:
                            # Division detection
                            divisions, confidence = detect_divisions(para)
                            all_divisions.update(divisions)

                            paragraphs_with_pages.append({
                                "text": para,
                                "page": i,
                                "division": divisions,
                                "confidence": confidence
                            })

            return {
                "status": "success",
                "content": markdown_content,
                "paragraphs": paragraphs_with_pages,
                "output_path": str(output_file),
                "filename": pdf_path.name,
                "pages": num_pages,
                "all_divisions": sorted(list(all_divisions), key=lambda x: int(x) if x.isdigit() else 0)
            }

        except Exception as e:
            error_msg = str(e)
            if config.VERBOSE:
                print(f"[ERROR] Hata: {error_msg}")

            return {
                "status": "error",
                "error": error_msg,
                "filename": pdf_path.name
            }


def main():
    """Test: İnput klasöründeki tüm PDF'leri parse et"""

    parser = PDFParser()
    pdf_files = list(config.INPUT_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"[WARN] {config.INPUT_DIR} klasorunde PDF yok")
        return

    print(f"[INFO] {len(pdf_files)} PDF bulundu\n")

    results = []
    for pdf_file in pdf_files:
        result = parser.parse(pdf_file)
        results.append(result)

    success_count = len([r for r in results if r['status'] == 'success'])
    print(f"\n[OK] {success_count} PDF basariyla parse edildi")


if __name__ == "__main__":
    main()