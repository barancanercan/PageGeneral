# 🎖️ PageGeneral - Day 2

**Tarihsel Belgeleri Analiz Eden Local RAG Sistemi**

## 🎯 Day 2 - LLM-Based Division Extraction

```
PDF → Paragraph by Paragraph
    ↓
LLM: "Bu paragrafta hangi tümenleri?"
    ↓
Per-Division Chromadb
    ↓
Semantic Search + Answer
    ↓
Berke formatında çıktı
```

---

## ⚡ Quick Start (5 dakika)

### Gereksinimler
- Python 3.10+
- 8GB RAM
- Ollama (lokal LLM)

### 1️⃣ Kurulum

```bash
# Clone
git clone <repo>
cd pagegeneral

# Virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Dependencies
pip install -r requirements.txt

# Ollama + Model (Terminal 1)
ollama pull qwen2.5:7b
ollama serve
```

### 2️⃣ PDF Ekle

```bash
cp /path/to/belgeler.pdf data/input/
```

### 3️⃣ Çalıştır (Terminal 2)

```bash
python scripts/query.py
```

**Output:**
```
🎖️  PAGEGENERAL - İnteraktif Sorgu Sistemi

📍 BULUNAN TÜMENLERI:
  1. 4. Piyade Tümeni
  2. 5. Piyade Tümeni
  3. 23. Piyade Tümeni
  4. 24. Piyade Tümeni
  5. 7. Piyade Tümeni
  6. 9. Piyade Tümeni

❓ Tümeni Seç (1-6 veya 'hepsi'): 1
❓ Sorun: Bu tümen nerede savaştı?

💬 CEVAP (4. Piyade Tümeni):
[LLM cevabı]

📍 KAYNAKLAR:
📄 Türk İstiklal Harbi - Mondros Mütarekesi, Sayfa 14
   Güven: 95%
   ID: parag_5
```

---

## 🏗️ Mimarisi

### Components

| Dosya | İşlev |
|-------|-------|
| `config.py` | Tümen listesi + ayarlar |
| `src/pdf_parser.py` | PDF → Text (pypdf) |
| `src/division_extractor.py` | LLM-based extraction |
| `src/chunker.py` | Chunks + metadata |
| `src/vector_store.py` | Chromadb ingestion |
| `src/query_engine.py` | Search + answer |
| `scripts/query.py` | Interactive UI |

### Flow

```
1️⃣ PDF Yükle
   pdf_parser.parse() → Text

2️⃣ Paragraf Böl
   text.split('\n\n') → [para1, para2, ...]

3️⃣ LLM Extraction
   DivisionExtractor.extract() → {
       para_id: 5,
       divisions: ["4. Piyade Tümeni"],
       confidence: 0.95
   }

4️⃣ Chunks + Metadata
   SmartChunker.create_chunks() → {
       id: "parag_5",
       document: "...",
       metadata: {
           division: [...],
           confidence: 0.95,
           source_page: 14,
           book_name: "...",
           book_id: "..."
       }
   }

5️⃣ Chromadb
   VectorStore.ingest_chunks() → Per-division DBs

6️⃣ Query
   QueryEngine.query() → Berke formatında
```

---

## 🧪 Test Etme

### PDF Parser Test

```bash
python src/pdf_parser.py
```

### LLM Connection Test

```bash
python src/llm.py
```

### Division Extraction Test

```bash
python src/division_extractor.py
```

### Vector Store Test

```bash
python src/vector_store.py
```

### Full Pipeline Test

```bash
python src/rag_pipeline.py
```

### Query Engine Test

```bash
python src/query_engine.py
```

---

## 📊 Çıktı Formatı (Berke)

```json
{
    "question": "Bu tümen nerede savaştı?",
    "division": "4. Piyade Tümeni",
    "answer": "LLM cevabı...",
    "sources": [
        {
            "id": "parag_5",
            "embedding": [0.0123, -0.98, ...],
            "document": "Paragraf metni...",
            "metadata": {
                "division": ["4. Piyade Tümeni"],
                "confidence": 0.95,
                "source_page": 14,
                "book_name": "Türk İstiklal Harbi - Mondros Mütarekesi",
                "book_id": "turk_istiklal_harbi_mondros"
            }
        }
    ],
    "timestamp": "2026-01-05T13:00:00"
}
```

---

## 🚨 Sorun Giderme

### "Ollama sunucusu çalışmıyor"
```bash
# Terminal 1'de çalıştır
ollama serve
```

### "PDF bulunamadı"
```bash
# PDF'leri data/input/ klasörüne ekle
cp /path/to/*.pdf data/input/
```

### "Model yüklenmedi"
```bash
# Model indir
ollama pull qwen2.5:7b
```

### "Chromadb hatası"
```bash
# Cache'i temizle
rm -rf chroma_db/
python scripts/query.py  # Yeniden başlat
```

---

## 📈 Performans

| İşlem | Zaman |
|-------|-------|
| PDF Parse | 2-5 sec |
| LLM Extraction | 30-60 sec (paragraf başına) |
| Embedding | 5-10 sec |
| Chromadb Ingestion | 10-20 sec |
| **Toplam (ilk çalışma)** | **2-3 minutes** |
| Query (search + answer) | **5-15 sec** |

---

## 🔧 Konfigürasyon

`config.py` dosyasında değiştir:

```python
# Tümen listesi (geçici)
DIVISION_LIST = [
    "4. Piyade Tümeni",
    "5. Piyade Tümeni",
    ...
]

# LLM
LLM_MODEL = "qwen2.5:7b"  # Türkçe optimized
LLM_TEMPERATURE = 0.1      # Düşük = daha deterministik

# Extraction
EXTRACTION_CONFIDENCE_THRESHOLD = 0.5  # 0.5'ten düşük skip

# Search
SEARCH_TOP_K = 5  # Kaç dokuman dönsün
```

---

## 🚀 Gelecek (Day 3+)

### v0.3 - Agentic Workflows
```python
class OfficerSearchAgent:
    "Hangi subaylar 4. Tümende?"

class BattleAnalysisAgent:
    "4. Tümen hangi savaşlara katıldı?"

class ComparisonAgent:
    "4. vs 9. Tümen farkları?"
```

### v0.4 - UI & API
- Streamlit web interface
- FastAPI endpoints
- Batch processing

---

## 📝 Lisans

MIT License - Özgürce kullan, değiştir, dağıt

---

```
╔════════════════════════════════════════╗
║  🎖️ PageGeneral - Day 2 ✅            ║
║  PDF → LLM → Chromadb → Query         ║
║  Status: Fully Functional              ║
║  Ready for: Agents & API               ║
╚════════════════════════════════════════╝
```

**via Baran Can Ercan** 🚀