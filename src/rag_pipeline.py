"""
PAGEGENERAL - RAG Pipeline
Ana sistem: PDF yükle → Metin işle → LLM'ye sor → Cevap dön
Minimal MVP. Vector DB yok şimdilik.
"""

from pathlib import Path
from src.pdf_parser import PDFParser
from src.llm import OllamaClient
import config
import json
from datetime import datetime


class TextChunker:
    """Metni basit cümlelere göre chunks'a böl"""

    @staticmethod
    def chunk(text: str, chunk_size: int = 512) -> list[dict]:
        """
        Metni chunk'lar (yaklaşık 512 token)

        Args:
            text: Tüm metin
            chunk_size: Chunk boyutu (token)

        Returns:
            List of chunks with metadata
        """
        # Basit: paragraflara göre böl
        paragraphs = text.split('\n\n')

        chunks = []
        current_chunk = ""
        chunk_id = 0

        for para in paragraphs:
            if not para.strip():
                continue

            # Eğer chunk dolu ise, kaydet
            if len(current_chunk) > chunk_size and current_chunk.strip():
                chunks.append({
                    "id": chunk_id,
                    "text": current_chunk.strip(),
                    "size": len(current_chunk)
                })
                chunk_id += 1
                current_chunk = ""

            current_chunk += para + "\n\n"

        # Son chunk'ı ekle
        if current_chunk.strip():
            chunks.append({
                "id": chunk_id,
                "text": current_chunk.strip(),
                "size": len(current_chunk)
            })

        return chunks


class RAGPipeline:
    """Ana RAG sistemi"""

    def __init__(self):
        self.parser = PDFParser()
        self.llm = OllamaClient()
        self.chunker = TextChunker()

    def ingest_pdf(self, pdf_path: str | Path) -> dict:
        """
        PDF'i yükle ve işle

        Returns:
            {
                "status": "success" | "error",
                "chunks": metin chunks'ları,
                "content": orijinal metin,
                "filename": dosya adı
            }
        """
        pdf_path = Path(pdf_path)

        # PDF'i parse et
        parse_result = self.parser.parse(pdf_path)

        if parse_result['status'] != 'success':
            return {"status": "error", "error": parse_result.get('error')}

        content = parse_result['content']

        # Metni chunks'a böl
        chunks = self.chunker.chunk(content, chunk_size=config.CHUNK_SIZE)

        if config.VERBOSE:
            print(f"✂️  {len(chunks)} chunk oluşturuldu")

        return {
            "status": "success",
            "chunks": chunks,
            "content": content,
            "filename": parse_result['filename'],
            "pages": parse_result.get('pages', 0)
        }

    def query(self, question: str, context: str) -> dict:
        """
        Soru sor ve cevap al

        Args:
            question: Kullanıcının sorusu
            context: Bağlam (PDF'den çıkan metin)

        Returns:
            {
                "question": soru,
                "answer": cevap,
                "sources": kaynak chunks,
                "confidence": 0.0-1.0,
                "timestamp": zaman
            }
        """
        if config.VERBOSE:
            print(f"\n❓ Sorgu: {question}")

        # Basit: context'in tamamını bağlam olarak kullan
        # (İleri aşamada: semantic search yapacağız)

        prompt = f"""Verilen bağlamdan hareketle, soruyu cevaplayınız.

BAĞLAM:
{context[:2000]}  # İlk 2000 karakter

SORU:
{question}

CEVAPLARıNız TÜRKÇE olmalı ve sadece bağlamdan bilgi kullanmalısınız.
Eğer bağlamda cevap yoksa "Bu konuda verilen belgede bilgi bulunmamaktadır" deyin."""

        # LLM'den cevap al
        answer = self.llm.generate(prompt)

        if not answer:
            return {
                "status": "error",
                "error": "LLM sunucusu yanıt vermedi. Ollama açık mı?"
            }

        if config.VERBOSE:
            print(f"💬 Cevap alındı ({len(answer)} karakter)")

        return {
            "status": "success",
            "question": question,
            "answer": answer,
            "context_length": len(context),
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.7  # Basit: sabit değer
        }

    def save_result(self, result: dict, output_file: Path = None):
        """Sonucu JSON'a kaydet"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = config.OUTPUT_DIR / f"result_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        if config.VERBOSE:
            print(f"💾 Kaydedildi: {output_file}")

        return output_file


def main():
    """Test"""

    pipeline = RAGPipeline()

    # PDF'leri yükle
    pdf_files = list(config.INPUT_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"⚠️  {config.INPUT_DIR} klasöründe PDF yok")
        return

    print(f"🔍 {len(pdf_files)} PDF bulundu\n")

    # İlk PDF'i yükle
    pdf_file = pdf_files[0]
    print(f"📥 Yükleniyor: {pdf_file.name}")

    ingest_result = pipeline.ingest_pdf(pdf_file)

    if ingest_result['status'] != 'success':
        print(f"❌ Hata: {ingest_result['error']}")
        return

    content = ingest_result['content']
    chunks = ingest_result['chunks']

    print(f"✅ Başarılı: {len(chunks)} chunk")

    # Test sorusu sor
    question = "Belgede ne anlatılıyor?"

    print(f"\n❓ Sorgu: {question}")

    query_result = pipeline.query(question, content)

    if query_result['status'] == 'success':
        print(f"\n💬 Cevap:\n{query_result['answer']}")

        # Kaydet
        pipeline.save_result(query_result)
    else:
        print(f"❌ {query_result['error']}")


if __name__ == "__main__":
    main()