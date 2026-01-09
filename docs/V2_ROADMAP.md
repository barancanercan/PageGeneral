# PageGeneral v2 - Product Roadmap

> Bu döküman Claude ile vibe coding için hazırlanmıştır.
> Tüm geliştirme bu dökümana göre yapılacaktır.

---

## Mevcut Durum (v1 - Tamamlandı)

```
✅ PDF → Metin çıkarma (sayfa bilgisi ile)
✅ Regex pre-filter + LLM hybrid extraction
✅ Dinamik confidence scoring (0.0-1.0)
✅ Doğru sayfa numarası tracking
✅ JSON output formatı
```

**Çalışan Pipeline:**
```
PDF → PDFParser → paragraphs[] → DivisionExtractor → JSON
```

---

## v2 Hedef Mimari

### Temel Prensipler

| Prensip | Açıklama |
|---------|----------|
| **Lokal & Bedava** | Tüm işlemler lokalde, API maliyeti yok |
| **No Over-engineering** | Minimum kod, maksimum iş |
| **Hızlı** | Gereksiz işlem tekrarı yok |
| **Dinamik** | N kitap, M sorgu destekli |

---

## Sistem Akışı

```
┌─────────────────────────────────────────────────────────────────┐
│                         PHASE 1: INGEST                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   [PDF Upload] → [Text Extract] → [Chunk] → [Embed] → [VectorDB] │
│        ↓              ↓              ↓          ↓          ↓      │
│     Arayüz      PDFParser     Paragraflar   HF Model   ChromaDB   │
│                                                                   │
│   ⚠️ Kitap zaten VDB'de varsa → SKIP (hash check)                │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        PHASE 2: EXTRACT                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   [Kitap Seç] → [Query Tanımla] → [VDB Search] → [LLM] → [Output]│
│        ↓              ↓                ↓           ↓        ↓     │
│   Multi-select   "Tümenler"      Similarity    Qwen2.5   JSON/CSV │
│   veya "Hepsi"   veya custom      Search                          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Detaylı Komponent Tasarımı

### 1. Book Registry (Kitap Kaydı)

**Amaç:** Hangi kitapların işlendiğini takip et, tekrar işlemeyi engelle.

```python
# SQLite veya basit JSON dosyası
{
    "books": [
        {
            "id": "abc123",  # MD5 hash of PDF
            "filename": "kitap1.pdf",
            "title": "Türk İstiklal Harbi",
            "pages": 370,
            "paragraphs": 335,
            "ingested_at": "2024-01-09T13:00:00",
            "status": "ready"  # pending | processing | ready | error
        }
    ]
}
```

**Dosya:** `data/registry.json`

---

### 2. Vector Database

**Seçim:** ChromaDB (lokal, embedded, hızlı)

**Neden ChromaDB?**
- Kurulum: `pip install chromadb`
- Sunucu gerektirmez
- Persistent storage
- Metadata filtering (kitap bazlı arama)

**Schema:**
```python
collection.add(
    ids=["book1_para_5"],
    documents=["Paragraf metni..."],
    embeddings=[[0.1, 0.2, ...]],  # 384-dim veya 768-dim
    metadatas=[{
        "book_id": "abc123",
        "book_name": "Türk İstiklal Harbi",
        "page": 241,
        "para_index": 5
    }]
)
```

---

### 3. Embedding Model

**Seçim:** `sentence-transformers/all-MiniLM-L6-v2`

**Neden?**
- 384 boyut (hızlı)
- 80MB model (hafif)
- Türkçe destekli (multilingual alternatif: `paraphrase-multilingual-MiniLM-L12-v2`)

**Alternatif (daha iyi Türkçe):**
- `emrecan/bert-base-turkish-cased-mean-nli-stsb-tr`

---

### 4. Arayüz

**Seçim:** Gradio (hızlı, basit, lokal)

**Neden Gradio?**
- `pip install gradio`
- 50 satır kodla full UI
- File upload built-in
- Lokal çalışır

**Alternatif:** Streamlit (daha fazla kontrol ama daha fazla kod)

---

## Dosya Yapısı (v2)

```
PageGeneral/
├── config.py                 # Tüm config
├── requirements.txt
├── app.py                    # 🆕 Gradio arayüz (entry point)
│
├── src/
│   ├── pdf_parser.py         # ✅ Mevcut
│   ├── llm.py                # ✅ Mevcut
│   ├── division_extractor.py # ✅ Mevcut
│   ├── embedder.py           # 🆕 Embedding işlemleri
│   ├── vector_store.py       # 🆕 ChromaDB wrapper
│   ├── registry.py           # 🆕 Kitap kayıt sistemi
│   └── extractor.py          # 🆕 Genel extraction logic
│
├── data/
│   ├── input/                # PDF'ler
│   ├── processed/            # Markdown cache
│   ├── vectordb/             # 🆕 ChromaDB persistent storage
│   └── registry.json         # 🆕 Kitap registry
│
├── output/                   # Extraction sonuçları
├── tests/
└── docs/
    └── V2_ROADMAP.md         # Bu dosya
```

---

## API Tasarımı

### Registry API

```python
class BookRegistry:
    def exists(self, pdf_path: Path) -> bool
    def add(self, pdf_path: Path, metadata: dict) -> str  # returns book_id
    def get(self, book_id: str) -> dict
    def list_all(self) -> List[dict]
    def delete(self, book_id: str) -> bool
```

### VectorStore API

```python
class VectorStore:
    def add_book(self, book_id: str, paragraphs: List[dict]) -> int  # returns count
    def search(self, query: str, book_ids: List[str] = None, top_k: int = 10) -> List[dict]
    def delete_book(self, book_id: str) -> bool
    def get_book_stats(self, book_id: str) -> dict
```

### Extractor API

```python
class Extractor:
    def extract(
        self,
        query: str,  # "Tümenler", "Komutanlar", custom...
        book_ids: List[str] = None,  # None = hepsi
        output_format: str = "json"  # json | csv | markdown
    ) -> Union[dict, str]
```

---

## Arayüz Tasarımı (Gradio)

### Tab 1: Kitap Yükle

```
┌────────────────────────────────────────────┐
│  📚 Kitap Yükle                            │
├────────────────────────────────────────────┤
│                                            │
│  [  PDF Dosyası Seç  ] [Yükle]            │
│                                            │
│  ─────────────────────────────────         │
│  📖 Yüklü Kitaplar:                        │
│  ┌──────────────────────────────────────┐  │
│  │ ☑ Türk İstiklal Harbi (370 sayfa)   │  │
│  │ ☑ Kurtuluş Savaşı (250 sayfa)       │  │
│  │ ☐ Çanakkale Savaşları (180 sayfa)   │  │
│  └──────────────────────────────────────┘  │
│                                            │
│  Status: ✅ 3 kitap hazır                  │
│                                            │
└────────────────────────────────────────────┘
```

### Tab 2: Bilgi Çıkar

```
┌────────────────────────────────────────────┐
│  🔍 Bilgi Çıkar                            │
├────────────────────────────────────────────┤
│                                            │
│  Kitap Seç: [Hepsi ▼] veya multi-select   │
│                                            │
│  Ne arıyorsun?                             │
│  ┌──────────────────────────────────────┐  │
│  │ Tümenleri ve konuşlanma yerlerini    │  │
│  │ bul                                   │  │
│  └──────────────────────────────────────┘  │
│                                            │
│  Çıktı Formatı: [JSON ▼]                   │
│                                            │
│  [  🚀 Çıkar  ]                            │
│                                            │
│  ─────────────────────────────────         │
│  Sonuçlar:                                 │
│  ┌──────────────────────────────────────┐  │
│  │ {                                     │  │
│  │   "results": [...]                    │  │
│  │ }                                     │  │
│  └──────────────────────────────────────┘  │
│                                            │
│  [📥 İndir]                                │
│                                            │
└────────────────────────────────────────────┘
```

---

## Geliştirme Sırası (Sprint Plan)

### Sprint 1: Core Infrastructure
```
[ ] 1.1 ChromaDB entegrasyonu (vector_store.py)
[ ] 1.2 Embedding model entegrasyonu (embedder.py)
[ ] 1.3 Book registry sistemi (registry.py)
[ ] 1.4 PDF hash check (duplicate detection)
```

### Sprint 2: Ingest Pipeline
```
[ ] 2.1 PDF → Paragraphs → Embeddings → VectorDB pipeline
[ ] 2.2 Progress tracking
[ ] 2.3 Error handling
[ ] 2.4 Test: Tek kitap ingest
```

### Sprint 3: Extraction Pipeline
```
[ ] 3.1 VectorDB search
[ ] 3.2 LLM extraction (mevcut kodu adapte et)
[ ] 3.3 Multi-book filtering
[ ] 3.4 Output formatları (JSON, CSV, Markdown)
```

### Sprint 4: Gradio UI
```
[ ] 4.1 Tab 1: Upload & Registry
[ ] 4.2 Tab 2: Search & Extract
[ ] 4.3 Progress bars
[ ] 4.4 Download buttons
```

### Sprint 5: Polish
```
[ ] 5.1 Performance optimization
[ ] 5.2 Error messages (Türkçe)
[ ] 5.3 README güncelle
[ ] 5.4 Demo video/gif
```

---

## Teknik Kararlar

### Embedding Batch Size
```python
EMBEDDING_BATCH_SIZE = 32  # Memory vs speed trade-off
```

### Chunk Strategy
```
Mevcut: Paragraf bazlı (iyi çalışıyor, değiştirme)
Alternatif: Sliding window (gerekirse)
```

### VectorDB Top-K
```python
DEFAULT_TOP_K = 20  # Daha fazla context, LLM filtreler
```

### Duplicate Detection
```python
# Basit: MD5 hash of file
# Gelişmiş: Content hash (ilk 1000 karakter)
import hashlib
book_id = hashlib.md5(pdf_path.read_bytes()).hexdigest()[:12]
```

---

## Performans Hedefleri

| İşlem | Hedef Süre |
|-------|------------|
| PDF Parse (100 sayfa) | < 5 sn |
| Embedding (100 paragraf) | < 10 sn |
| VectorDB Insert | < 1 sn |
| Search (10K paragraf) | < 500ms |
| LLM Extraction (20 paragraf) | < 30 sn |

---

## Bağımlılıklar (requirements.txt güncelleme)

```
# Mevcut
pypdf>=4.0.0
transformers>=4.36.0
torch>=2.0.0
huggingface_hub>=0.20.0
tqdm>=4.66.0

# Yeni (v2)
chromadb>=0.4.0
sentence-transformers>=2.2.0
gradio>=4.0.0
```

---

## Notlar (Claude için)

1. **Mevcut kodu koru:** `pdf_parser.py`, `llm.py`, `division_extractor.py` çalışıyor. Gereksiz değiştirme.

2. **Incremental geliştir:** Her sprint sonunda çalışan bir şey olmalı.

3. **Test et:** Her yeni modül için basit test yaz.

4. **Hata mesajları:** Türkçe ve anlaşılır olsun.

5. **Config merkezli:** Tüm sabitler `config.py`'de olsun.

6. **No magic numbers:** Her sayı bir sabit olsun.

7. **Logging:** `print` yerine proper logging (ama basit tut).

---

## Başlangıç Komutu

```bash
# v2 geliştirmeye başlarken
git checkout -b v2-product
```

---

*Son güncelleme: 2024-01-09*
*Versiyon: v2.0-draft*