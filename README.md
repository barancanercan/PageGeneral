<p align="center">
  <img src="logo/logo.png" alt="PageGeneral Logo" width="180">
</p>

<h1 align="center">PageGeneral</h1>

<p align="center">
  <strong>Tarihi Askeri Belgelerden Tumen Bilgisi Cikarma Araci</strong>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python"></a>
  <a href="https://streamlit.io/"><img src="https://img.shields.io/badge/Streamlit-1.28+-red.svg" alt="Streamlit"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"></a>
</p>

<p align="center">
  <a href="#ozellikler">Ozellikler</a> •
  <a href="#kurulum">Kurulum</a> •
  <a href="#kullanim">Kullanim</a> •
  <a href="#api">API</a> •
  <a href="#deploy">Deploy</a>
</p>

---

## Hakkinda

**PageGeneral**, tarihi Turk askeri belgelerinden (PDF) tumen ve firka bilgilerini otomatik olarak cikarip yapilandirilmis veri olarak sunan bir NLP aracidir. Semantic embedding ve vector database teknolojileri kullanarak belgeleri akilli bir sekilde isler.

## Ozellikler

| Ozellik | Aciklama |
|---------|----------|
| **PDF Parsing** | Cok sayfalı PDF belgelerini otomatik parse etme |
| **Tumen Tespiti** | Regex tabanli tumen/firka referans tespiti |
| **Semantic Embedding** | sentence-transformers ile 384 boyutlu vektorler |
| **Vector Database** | ChromaDB ile hizli semantic arama |
| **JSON Export** | Embedding dahil yapilandirilmis cikti |
| **Web Arayuzu** | Kullanici dostu Streamlit arayuzu |

## Teknoloji Stack

<p align="center">
  <img src="https://img.shields.io/badge/pypdf-PDF%20Parser-orange?style=for-the-badge" alt="pypdf">
  <img src="https://img.shields.io/badge/ChromaDB-Vector%20DB-purple?style=for-the-badge" alt="ChromaDB">
  <img src="https://img.shields.io/badge/PyTorch-ML%20Framework-red?style=for-the-badge" alt="PyTorch">
  <img src="https://img.shields.io/badge/Streamlit-Web%20UI-ff4b4b?style=for-the-badge" alt="Streamlit">
</p>

## Kurulum

### Gereksinimler

- Python 3.10+
- pip

### Adimlar

```bash
# 1. Repo'yu klonlayin
git clone https://github.com/barancanercan/PageGeneral.git
cd PageGeneral

# 2. Virtual environment olusturun
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# 3. Bagimliliklari yukleyin
pip install -r requirements.txt
```

## Kullanim

### Web Arayuzu

```bash
streamlit run streamlit_app.py
```

Tarayicinizda `http://localhost:8501` adresini acin.

**Ozellikler:**
- PDF yukleme ve islem
- Paragraf goruntuleyici
- Tumen filtreleme
- JSON indirme

### CLI

```bash
# PDF'leri VectorDB'ye yukle
python run.py ingest

# Tumen listesini gor
python run.py query -l

# JSON olarak export et
python run.py query -d
```

## API

### Cikti Formati

```json
{
  "id": "parag_5",
  "embedding": [0.0123, -0.0456, ...],
  "document": "5 nci Kafkas Tumeni Sarikamis'ta konuslanmistir.",
  "metadata": {
    "division": ["5"],
    "confidence": 0.95,
    "source_page": 27
  }
}
```

| Alan | Tip | Aciklama |
|------|-----|----------|
| `id` | string | Paragraf ID |
| `embedding` | float[384] | Semantic vektor |
| `document` | string | Paragraf metni |
| `metadata.division` | string[] | Tespit edilen tumenler |
| `metadata.confidence` | float | Guven skoru (0-1) |
| `metadata.source_page` | int | Kaynak sayfa numarasi |

## Proje Yapisi

```
PageGeneral/
├── streamlit_app.py     # Web arayuzu
├── run.py               # CLI arayuzu
├── config.py            # Konfigurasyonlar
├── requirements.txt     # Python bagimliliklari
│
├── src/
│   ├── pdf_parser.py    # PDF parse + division detection
│   ├── embedder.py      # Sentence-transformers wrapper
│   ├── vector_store.py  # ChromaDB operations
│   ├── ingest.py        # PDF -> VectorDB pipeline
│   └── query.py         # VectorDB -> JSON export
│
├── data/
│   ├── input/           # PDF dosyalari
│   └── vectordb/        # ChromaDB verileri
│
├── output/              # JSON ciktilar
└── logo/                # Proje logosu
```

## Deploy

### Streamlit Cloud

1. GitHub'a push edin
2. [share.streamlit.io](https://share.streamlit.io) adresine gidin
3. **New app** > Repo secin > `streamlit_app.py` secin
4. **Deploy!**

> **Not:** Ilk deploy'da model indirme islemi birkaç dakika surebilir.

### Local Production

```bash
streamlit run streamlit_app.py --server.port 8501 --server.headless true
```

## Lisans

Bu proje [MIT Lisansi](LICENSE) altinda lisanslanmistir.

---

<p align="center">
  <sub>Built with Python & Streamlit by Baran Can Ercan</sub>
</p>
