<p align="center">
  <img src="logo/logo.png" alt="PageGeneral Logo" width="200">
</p>

# PageGeneral

PDF'lerden tumen bilgisi cikarma araci. Tarihi Turk askeri belgelerinden tumen/firka bilgilerini otomatik olarak cikarir.

## Ozellikler

- PDF'leri otomatik parse etme
- Tumen/firka referanslarini tespit etme (regex tabanli)
- Semantic embedding olusturma (sentence-transformers)
- VectorDB depolama (ChromaDB)
- JSON export (embedding dahil)
- Streamlit web arayuzu

## Kurulum

```bash
# Clone
git clone https://github.com/barancanercan/PageGeneral.git
cd PageGeneral

# Virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Dependencies
pip install -r requirements.txt
```

## Kullanim

### Web Arayuzu (Streamlit)

```bash
streamlit run streamlit_app.py
```

Tarayicida `http://localhost:8501` adresini acin.

### CLI

```bash
# PDF'leri VectorDB'ye yukle
python run.py ingest

# Tumen listesi
python run.py query -l

# JSON export
python run.py query -d
```

## Cikti Formati

```json
{
  "id": "parag_5",
  "embedding": [384 deger...],
  "document": "5 nci Kafkas Tumeni Sarikamis'ta...",
  "metadata": {
    "division": ["5"],
    "confidence": 0.95,
    "source_page": 27
  }
}
```

## Proje Yapisi

```
PageGeneral/
├── streamlit_app.py    # Web UI
├── run.py              # CLI
├── config.py           # Ayarlar
├── requirements.txt
├── .streamlit/         # Streamlit config
│   └── config.toml
├── src/
│   ├── pdf_parser.py   # PDF parse + division detection
│   ├── embedder.py     # Sentence-transformers embedding
│   ├── vector_store.py # ChromaDB
│   ├── ingest.py       # PDF -> VectorDB
│   └── query.py        # VectorDB -> JSON
├── data/
│   ├── input/          # PDF'ler buraya
│   └── vectordb/       # ChromaDB verileri
└── output/             # JSON ciktilar
```

## Teknolojiler

- **PDF**: pypdf
- **Embedding**: sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
- **VectorDB**: ChromaDB
- **UI**: Streamlit
- **ML**: PyTorch

## Streamlit Cloud Deploy

1. GitHub'a push edin:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. [share.streamlit.io](https://share.streamlit.io) adresine gidin

3. "New app" tiklayin

4. Ayarlar:
   - Repository: `barancanercan/PageGeneral`
   - Branch: `main`
   - Main file path: `streamlit_app.py`

5. "Deploy!" tiklayin

**Not**: Ilk deploy sirasinda sentence-transformers modeli indirilecegi icin birkaç dakika bekleyebilir.

## Local Deploy

```bash
streamlit run streamlit_app.py --server.port 8501
```

## Lisans

MIT
