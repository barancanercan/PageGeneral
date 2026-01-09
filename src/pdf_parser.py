"""
PAGEGENERAL - PDF Parser (Hafif Versiyon)
pypdf ile basit metin çıkarma. 2 saniye.
Docling'in OCR/layout/tablo bloatı yok.
"""

from pathlib import Path
from pypdf import PdfReader
import config


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
                print(f"📄 Parse ediliyor: {pdf_path.name}")

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
                print(f"✅ Kaydedildi: {output_file}")

            # Sayfa bazlı paragrafları çıkar
            paragraphs_with_pages = []
            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text and text.strip():
                    # Her sayfadaki paragrafları ayır
                    page_paragraphs = text.strip().split('\n\n')
                    for para in page_paragraphs:
                        para = para.strip()
                        if para:
                            paragraphs_with_pages.append({
                                "text": para,
                                "page": i
                            })

            return {
                "status": "success",
                "content": markdown_content,
                "paragraphs": paragraphs_with_pages,
                "output_path": str(output_file),
                "filename": pdf_path.name,
                "pages": num_pages
            }

        except Exception as e:
            error_msg = str(e)
            if config.VERBOSE:
                print(f"❌ Hata: {error_msg}")

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
        print(f"⚠️  {config.INPUT_DIR} klasöründe PDF yok")
        return

    print(f"🔍 {len(pdf_files)} PDF bulundu\n")

    results = []
    for pdf_file in pdf_files:
        result = parser.parse(pdf_file)
        results.append(result)

    success_count = len([r for r in results if r['status'] == 'success'])
    print(f"\n✅ {success_count} PDF başarıyla parse edildi")


if __name__ == "__main__":
    main()