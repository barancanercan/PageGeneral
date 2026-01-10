"""
PageGeneral - Configuration
HuggingFace API settings for Qwen2.5-7B-Instruct
"""

import os
from pathlib import Path

# ============================================================================
# PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = PROJECT_ROOT / "output"

# v2 paths
VECTORDB_DIR = DATA_DIR / "vectordb"
REGISTRY_FILE = DATA_DIR / "registry.json"

# Create directories
for directory in [DATA_DIR, INPUT_DIR, PROCESSED_DIR, OUTPUT_DIR, VECTORDB_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# HUGGINGFACE API
# ============================================================================

HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_MODEL = "Qwen/Qwen2.5-7B-Instruct"

# LLM settings
LLM_TEMPERATURE = 0.1  # Dusuk = daha deterministik
LLM_MAX_TOKENS = 500

# ============================================================================
# DIVISIONS - Güncellenebilir tümen listesi
# ============================================================================

DIVISIONS_FILE = DATA_DIR / "divisions.json"

# Default division listesi
DEFAULT_DIVISIONS = [
    "5", "9", "10", "11", "12", "15", "23", "24", "27", "36", "41"
]

# Division pattern'leri (regex)
DIVISION_PATTERNS = [
    # Türkçe formatlar
    r'(\d{1,3})\s*(?:\'?n?(?:ci|nci|ncı|inci|ıncı|uncu|üncü))\s*(?:Kafkas\s+)?(?:Tümen|Tumen|Fırka|Firka|Süvari\s+Tümeni?)',
    r'(\d{1,3})\s*\.\s*(?:Kafkas\s+)?(?:Tümen|Tumen|Fırka|Firka|Süvari\s+Tümeni?)',
    # İngilizce formatlar
    r'(\d{1,3})(?:st|nd|rd|th)\s+(?:Caucasian\s+)?(?:Division|Infantry\s+Division|Cavalry\s+Division)',
    # Genel numerik
    r'(?:Division|Tümen|Tumen)\s+(?:No\.?\s*)?(\d{1,3})',
]

def load_divisions():
    """JSON dosyasından tümen listesini yükle"""
    import json
    if DIVISIONS_FILE.exists():
        with open(DIVISIONS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("divisions", DEFAULT_DIVISIONS)
    return DEFAULT_DIVISIONS

def save_divisions(divisions: list):
    """Tümen listesini JSON dosyasına kaydet"""
    import json
    with open(DIVISIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump({"divisions": divisions}, f, ensure_ascii=False, indent=2)

def add_division(div_num: str):
    """Yeni tümen ekle"""
    divisions = load_divisions()
    if div_num not in divisions:
        divisions.append(div_num)
        divisions.sort(key=lambda x: int(x) if x.isdigit() else 0)
        save_divisions(divisions)
    return divisions

def remove_division(div_num: str):
    """Tümen sil"""
    divisions = load_divisions()
    if div_num in divisions:
        divisions.remove(div_num)
        save_divisions(divisions)
    return divisions

# İlk çalıştırmada default dosyayı oluştur
if not DIVISIONS_FILE.exists():
    save_divisions(DEFAULT_DIVISIONS)

# ============================================================================
# EXTRACTION
# ============================================================================

EXTRACTION_CONFIDENCE_THRESHOLD = 0.5
VERBOSE = True

# ============================================================================
# v2 - EMBEDDING & VECTORDB
# ============================================================================

# Embedding model
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_BATCH_SIZE = 32

# ChromaDB
CHROMA_COLLECTION_NAME = "pagegeneral_docs"

# VectorDB search
DEFAULT_TOP_K = 20

# ============================================================================
# v2 - LOGGING
# ============================================================================

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
