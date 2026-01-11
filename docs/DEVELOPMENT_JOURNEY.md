# PageGeneral - Gelistirme Sureci Dokumantasyonu

Bu dokuman, PageGeneral projesinin gelistirme surecini, kullanilan teknolojileri, karsilasilan sorunlari ve cozumlerini basamak basamak anlatmaktadir.

---

## Icindekiler

1. [Proje Vizyonu](#1-proje-vizyonu)
2. [PDF Parsing Asamasi](#2-pdf-parsing-asamasi)
3. [Tumen Tespiti (NLP)](#3-tumen-tespiti-nlp)
4. [Embedding Olusturma](#4-embedding-olusturma)
5. [Vector Database Entegrasyonu](#5-vector-database-entegrasyonu)
6. [UI Gelistirme Sureci](#6-ui-gelistirme-sureci)
7. [Karsilasilan Sorunlar ve Cozumleri](#7-karsilasilan-sorunlar-ve-cozumleri)
8. [Deployment Hazirligi](#8-deployment-hazirligi)
9. [Ogrenilen Dersler](#9-ogrenilen-dersler)

---

## 1. Proje Vizyonu

### Hedef
Tarihi Turk askeri belgelerinden (PDF formatinda) tumen ve firka bilgilerini otomatik olarak cikarip, yapilandirilmis veri olarak sunmak.

### Istenen Cikti Formati
```json
{
  "id": "parag_5",
  "embedding": [384 boyutlu vektor],
  "document": "Paragraf metni",
  "metadata": {
    "division": ["5", "9"],
    "confidence": 0.95,
    "source_page": 27
  }
}
```

### Temel Gereksinimler
- PDF'leri parse edebilme
- Tumen/firka referanslarini tespit edebilme
- Semantic embedding olusturabilme
- Verileri veritabaninda saklayabilme
- JSON olarak export edebilme
- Kullanici dostu arayuz

---

## 2. PDF Parsing Asamasi

### Kullanilan Teknoloji
**pypdf** (v4.0+)

### Neden pypdf?
- Pure Python - ek sistem bagimliligi yok
- Aktif olarak gelistiriliyor
- Turkce karakter destegi iyi
- Sayfa sayfa okuma imkani

### Implementasyon
```python
from pypdf import PdfReader

def parse_pdf(file_path):
    reader = PdfReader(file_path)
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        # Paragraf ayirma
        paragraphs = text.split('\n\n')
```

### Ogrenilen
- PDF'lerin yapisal olarak tutarsiz olabilecegi
- Sayfa numarasi takibinin onemi
- Paragraf ayirma stratejilerinin zorluklari

---

## 3. Tumen Tespiti (NLP)

### Kullanilan Teknoloji
**Regex (Regular Expressions)**

### Neden Regex?
- Baslangiçta LLM (Qwen) denendi ancak:
  - API bagimliligi
  - Maliyet
  - Hiz sorunlari
- Regex daha hizli ve guvenilir

### Tumen Pattern'leri
```python
DIVISION_PATTERNS = [
    # Turkce formatlar
    r'(\d{1,3})\s*(?:\'?n?(?:ci|nci|ncı|inci|ıncı|uncu|üncü))\s*(?:Kafkas\s+)?(?:Tümen|Tumen|Fırka|Firka)',
    r'(\d{1,3})\s*\.\s*(?:Kafkas\s+)?(?:Tümen|Tumen|Fırka|Firka)',
    # Ingilizce formatlar
    r'(\d{1,3})(?:st|nd|rd|th)\s+(?:Division|Infantry\s+Division)',
]
```

### Confidence Skorlama
```python
def calculate_confidence(text, divisions):
    # Birden fazla match = daha yuksek guven
    # Context keywords = bonus puan
    # Tek match = orta guven
```

### Ogrenilen
- Tarihi belgelerdeki farkli yazim sekilleri
- Turkce'nin ek yapisiyla basa cikma
- Pattern'lerin surekli genisletilmesi gerektigi

---

## 4. Embedding Olusturma

### Kullanilan Teknoloji
**sentence-transformers** (paraphrase-multilingual-MiniLM-L12-v2)

### Neden Bu Model?
- Cok dilli destek (Turkce dahil)
- 384 boyutlu vektor (dengeli boyut)
- Hizli inference
- Ucretsiz ve acik kaynak

### Implementasyon
```python
from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(
            'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        )

    def embed(self, texts):
        return self.model.encode(texts, show_progress_bar=True)
```

### Ogrenilen
- Model ilk yuklemede internetten indiriliyor (~500MB)
- Batch processing performansi artiriyor
- GPU varsa otomatik kullaniliyor

---

## 5. Vector Database Entegrasyonu

### Kullanilan Teknoloji
**ChromaDB** (v0.4+)

### Neden ChromaDB?
- Kolay kurulum (pip install)
- Persistent storage
- Metadata filtreleme
- Semantic search built-in

### Implementasyon
```python
import chromadb

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="data/vectordb")
        self.collection = self.client.get_or_create_collection("documents")

    def add(self, ids, documents, embeddings, metadatas):
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
```

### Onemli Notlar
- ChromaDB metadata'da list desteklemiyor - string'e cevirmek gerekiyor
- Collection isimleri benzersiz olmali
- Persistent path onemli

### Ogrenilen
- Vector database kavramlari
- Embedding + metadata kombinasyonu
- Semantic search vs keyword search farki

---

## 6. UI Gelistirme Sureci

### Ilk Deneme: Gradio

**Kullanilan:** Gradio 4.x

**Avantajlar:**
- Hizli prototipleme
- ML modelleri icin optimize

**Karsilasilan Sorunlar:**
- `height` parametresi desteklenmiyordu
- UI cok karisik geliyordu
- Dataframe scroll sorunlari

### Final Cozum: Streamlit

**Kullanilan:** Streamlit 1.28+

**Neden Gecis Yapildi:**
- Daha temiz API
- Daha iyi dokumantasyon
- Deployment kolayligi (Streamlit Cloud)
- Daha profesyonel gorunum

**UI Yapisi:**
```python
import streamlit as st

st.set_page_config(page_title="PageGeneral", page_icon="logo/logo.png")

# Sidebar: Kitap yonetimi
with st.sidebar:
    st.header("Kitaplar")
    # Kitap secimi
    # PDF yukleme

# Ana alan: Paragraflar
st.dataframe(df, use_container_width=True)

# JSON indirme
st.download_button("JSON Indir", data=json_data)
```

### Ogrenilen
- Framework seciminin onemi
- Kullanici deneyimi (UX) dusunmek
- Basitligin gucu

---

## 7. Karsilasilan Sorunlar ve Cozumleri

### Sorun 1: PyTorch DLL Hatasi (Windows)

**Hata:**
```
OSError: [WinError 126] The specified module could not be found
Error loading "torch_cpu.dll"
```

**Cozum:**
Script basina torch import'u eklemek:
```python
try:
    import torch
except ImportError:
    pass
```

**Ogrenilen:** Windows'ta DLL yukleme sirasi onemli.

---

### Sorun 2: ChromaDB Bozulmasi

**Hata:**
```
sqlite3.DatabaseError: database disk image is malformed
```

**Cozum:**
```bash
rm -rf data/vectordb/
rm data/registry.json
```

**Ogrenilen:** Development sirasinda DB'yi temizlemek gerekebilir.

---

### Sorun 3: Unicode/Emoji Encoding Hatalari

**Hata:**
```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**Cozum:**
Emoji'leri ASCII ile degistirmek:
```python
# Onceki
print("✓ Basarili")

# Sonraki
print("[OK] Basarili")
```

**Ogrenilen:** Windows console UTF-8 ile sorun yasayabiliyor.

---

### Sorun 4: Gradio Dataframe height Parametresi

**Hata:**
```
TypeError: Dataframe.__init__() got unexpected keyword argument 'height'
```

**Cozum:**
```python
# Onceki
gr.Dataframe(height=400)

# Sonraki
gr.Dataframe(row_count=(20, "dynamic"))
```

**Ogrenilen:** Kutuphane versiyonlari arasi API farkliliklari.

---

### Sorun 5: NumPy Array Truth Value Hatasi

**Hata:**
```
ValueError: The truth value of an array with more than one element is ambiguous
```

**Cozum:**
```python
# Onceki
if results.get("embeddings"):

# Sonraki
if results.get("embeddings") is not None:
```

**Ogrenilen:** NumPy array'leri boolean context'te kullanmamak.

---

### Sorun 6: Streamlit Komutu Bulunamadi

**Hata:**
```
streamlit: The term 'streamlit' is not recognized
```

**Cozum:**
```bash
# Yontem 1: venv aktif et
.venv\Scripts\activate
streamlit run app.py

# Yontem 2: Python module olarak calistir
python -m streamlit run app.py
```

**Ogrenilen:** Virtual environment ve PATH yonetimi.

---

## 8. Deployment Hazirligi

### Olusturulan Dosyalar

**1. .streamlit/config.toml**
```toml
[theme]
primaryColor = "#1f77b4"

[server]
maxUploadSize = 200

[browser]
gatherUsageStats = false
```

**2. requirements.txt (Streamlit Cloud uyumlu)**
```
pypdf>=4.0.0
chromadb>=0.4.0
sentence-transformers>=2.2.0
streamlit>=1.28.0
pandas>=2.0.0
tqdm>=4.66.0
```

**3. .gitignore Guncellemeleri**
```
data/vectordb/
data/registry.json
.streamlit/secrets.toml
output/*.json
```

### Deployment Adimlari
1. GitHub'a push
2. share.streamlit.io'ya git
3. Repo sec
4. streamlit_app.py sec
5. Deploy!

---

## 9. Ogrenilen Dersler

### Teknik Dersler

1. **Basit Baslangic:** LLM yerine regex ile baslamak dogru karardi
2. **Framework Secimi:** Gradio'dan Streamlit'e gecis UX'i iyilestirdi
3. **Hata Yonetimi:** Her platformda farkli hatalar cikabilir
4. **Versiyon Uyumu:** Kutuphane versiyonlari onemli

### Proje Yonetimi Dersleri

1. **Iteratif Gelistirme:** Kucuk adimlarla ilerlemek
2. **Kullanici Geri Bildirimi:** UI'i kullaniciya gore sekillendirmek
3. **Dokumantasyon:** Her asamayi belgelemek

### Teknoloji Stack Ozeti

| Katman | Teknoloji | Versiyon |
|--------|-----------|----------|
| PDF Parsing | pypdf | 4.0+ |
| NLP/Regex | Python re | Built-in |
| Embedding | sentence-transformers | 2.2+ |
| Vector DB | ChromaDB | 0.4+ |
| UI Framework | Streamlit | 1.28+ |
| ML Backend | PyTorch | 2.0+ |

---

## Sonuc

PageGeneral projesi, PDF'lerden yapilandirilmis veri cikarma problemini cozemek icin modern NLP ve vector database teknolojilerini bir araya getirmektedir. Gelistirme surecinde karsilasilan zorluklar, ozellikle cross-platform uyumluluk ve UI/UX konularinda onemli dersler ogretmistir.

Proje, Streamlit Cloud uzerinde deploy edilmeye hazir durumdadir.

---

*Bu dokuman, PageGeneral v2 gelistirme surecini kapsamaktadir.*
*Son guncelleme: Ocak 2026*
