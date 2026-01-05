# 🎖️ PageGeneral

**Tarihsel Belgeleri Analiz Eden Local RAG Sistemi**

Harp belgelerini PDF'ten oku, Türkçe sorular sor, yapay zekadan cevap al. Tamamen lokal, ücretsiz, açık kaynak.

---

## ⚡ Quick Start

### Gereksinimler
- Python 3.10+
- 8GB RAM
- Ollama (lokal LLM)

### Kurulum (5 dakika)

```bash
# 1. Repository'i clone et
git clone https://github.com/yourusername/pagegeneral.git
cd pagegeneral

# 2. Virtual environment
python3.10 -m venv venv
source venv/bin/activate

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Ollama'yı indir ve modeli yükle (Terminal 1)
ollama pull qwen2.5:7b
ollama serve

# 5. PDF'leri data/input/ klasörüne koy

# 6. Sorgu sistemi (Terminal 2)
python scripts/query.py
```

### İlk Sorgu

```
❓ Sorun: Belgede ne anlatılıyor?

💬 Cevap: [LLM'nin Türkçe cevabı]
📊 Güven: 70%
💾 Sonuç kaydedildi: output/result_*.json
```

---

## ✅ Tamamlanan (v0.1 MVP)

- ✅ **PDF Parser** - `pypdf` ile hafif okuma (2 saniye)
- ✅ **LLM Client** - Ollama + qwen2.5:7b Türkçe desteği
- ✅ **RAG Pipeline** - PDF yükle → Chunk → LLM
- ✅ **İnteraktif Sorgu** - Terminal'de canlı Q&A
- ✅ **JSON Output** - Cevapları kaydet

### Mimarisi

```
PDF → Parser (pypdf) → Text Chunks → LLM (Ollama)
                                        ↓
                                    Cevap
                                        ↓
                                   JSON Output
```

### Dosya Yapısı

```
pagegeneral/
├── config.py                          # Sistem ayarları
├── src/
│   ├── pdf_parser.py                 # PDF okuma
│   ├── llm_client.py                 # Ollama bağlantısı
│   └── rag_pipeline.py               # Ana sistem
├── scripts/
│   └── query.py                      # İnteraktif sorgu
├── data/
│   ├── input/                        # ← PDF'ler buraya
│   ├── processed/                    # İşlenmiş markdown
│   └── cache/
├── output/                           # Sorgu sonuçları (JSON)
└── chroma_db/                        # [Yakında] Vector DB
```

---

## 🔄 Gelecek (v0.2+)

### v0.2 - Vector Database & Search
- [ ] Chromadb entegrasyonu
- [ ] Semantic search (embedding-based)
- [ ] Chunk-level retrieval
- [ ] Accuracy/F1 metrikleri

### v0.3 - Advanced Retrieval
- [ ] BM25 hybrid search (keyword + semantic)
- [ ] Cross-encoder reranking
- [ ] Multi-document support
- [ ] Citation sources

### v0.4 - UI & API
- [ ] Streamlit web UI
- [ ] FastAPI REST endpoints
- [ ] Batch query processing
- [ ] Export (PDF/Excel)

### v0.5+ - Production
- [ ] Docker containerization
- [ ] Fine-tuned Turkish LLM
- [ ] Performance optimization (GPU)
- [ ] Cloud deployment

---

## 🛠️ Teknik Stack

| Katman | Teknoloji | Not |
|--------|-----------|-----|
| PDF | `pypdf` | Hafif, hızlı |
| LLM | Ollama + qwen2.5:7b | Lokal, Türkçe |
| Search | [Yakında] Chromadb | Vector DB |
| Output | JSON | Basit, standard |
| CLI | Python | Minimal dependencies |

---

## 📖 Kullanım

### 1. PDF Yükle

```bash
cp /path/to/document.pdf data/input/
python scripts/query.py
```

### 2. Sorgu Sor

```
❓ Sorun: Belgede Mondros Mütarekesi ne zaman imzalandı?
❓ Sorgun: Belgede Mondros Mütarekesi ne zaman imzalandı?
🤖 LLM'ye soruluyor (qwen2.5:7b)...

💬 Cevap:
Belgede bu bilgi detaylı olarak açıklanmıştır...
```

### 3. Sonuç

```json
{
  "question": "...",
  "answer": "...",
  "confidence": 0.7,
  "timestamp": "2026-01-05T11:34:00"
}
```

---

## ⚙️ Yapılandırma

`config.py` dosyasında değiştir:

```python
# Model seçimi
LLM_MODEL = "qwen2.5:7b"  # Türkçe iyi
# veya
LLM_MODEL = "mistral"     # Daha hızlı

# Chunk boyutu
CHUNK_SIZE = 512          # Token cinsinden

# Ollama ayarları
OLLAMA_BASE_URL = "http://localhost:11434"
```

---

## 🔍 Sistem Gereksimleri

- **CPU:** Intel/AMD (8+ cores)
- **RAM:** 8GB+ (qwen2.5:7b için)
- **Disk:** 20GB (modeller + DB)
- **OS:** Linux, macOS, Windows (WSL2)

### Hız

| İşlem | Zaman |
|-------|-------|
| PDF okuma | 2 saniye |
| Text chunking | < 1 saniye |
| LLM yanıt | 5-30 saniye |
| **Toplam** | ~10-40 saniye |

---

## 🚀 Katkıda Bulun

```bash
# Fork et → Branch oluştur → Commit → Push → PR
git checkout -b feature/vector-db
git commit -m "Add chromadb support"
git push origin feature/vector-db
```

---

## 📝 Lisans

MIT License - Özgürce kullan, değiştir, dağıt

---


## 💬 İletişim

- 🐛 Sorun: GitHub Issues
- 💡 Soru: Discussions
- 📧 Email: barancanercan@gmail.com

---

## 🎖️ Roadmap Özeti

```
v0.1 ✅ MVP (PDF + LLM + Query)
  ↓
v0.2 🔄 Vector DB (Semantic Search)
  ↓
v0.3 📊 Advanced Search (BM25 + Reranking)
  ↓
v0.4 🎨 Web UI (Streamlit)
  ↓
v0.5 🚀 Production (Docker, API)
```

---

```
╔════════════════════════════════════════╗
║  PageGeneral - Tarihsel Verinin Komutanı ║
║  Local RAG | Free | Open Source         ║
╚════════════════════════════════════════╝
```

**Belgelerin konuşmaya başladığında, geçmiş aydınlanır.**