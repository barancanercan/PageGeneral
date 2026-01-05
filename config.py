"""
PAGEGENERAL - Sistem Konfigürasyonu
Minimal ve basit ayarlar. Sadece MVP için gerekli.
"""

from pathlib import Path

# ============================================================================
# TEMEL PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"              # PDF'ler buraya
PROCESSED_DIR = DATA_DIR / "processed"      # İşlenmiş markdown
CACHE_DIR = DATA_DIR / "cache"
OUTPUT_DIR = PROJECT_ROOT / "output"        # Sorgu sonuçları
CHROMA_DB_DIR = PROJECT_ROOT / "chroma_db"  # Vector database

# Klasörleri oluştur
for directory in [DATA_DIR, INPUT_DIR, PROCESSED_DIR, CACHE_DIR, OUTPUT_DIR, CHROMA_DB_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# LLM (OLLAMA) AYARLARI
# ============================================================================

OLLAMA_BASE_URL = "http://localhost:11434"
LLM_MODEL = "qwen2.5:7b"        # ← Türkçe için en iyi
LLM_TEMPERATURE = 0.1           # Düşük = daha deterministik
LLM_MAX_TOKENS = 500


# ============================================================================
# EMBEDDING AYARLARI (Docling için)
# ============================================================================

EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIMENSION = 384


# ============================================================================
# CHUNKING AYARLARI
# ============================================================================

CHUNK_SIZE = 512        # Token cinsinden
CHUNK_OVERLAP = 50


# ============================================================================
# ARAMA AYARLARI
# ============================================================================

BM25_TOP_K = 10         # Kaç belge al
SEMANTIC_TOP_K = 10
RERANK_TOP_K = 5        # Son kaç dokuman
FINAL_RETRIEVAL_K = 3   # Kaç sonuç döndür


# ============================================================================
# SİSTEM AYARLARI
# ============================================================================

STRICT_CONTEXT_MODE = True      # Yalnızca bağlamdan cevap ver
REQUIRE_CITATIONS = True        # Kaynakları göster
VERBOSE = True                  # Detaylı çıktı


# ============================================================================
# TÜRKÇE AYARLARI
# ============================================================================

TURKISH_STOPWORDS = {
    "ve", "ile", "bir", "bu", "o", "de", "da", "için",
    "olarak", "olan", "gibi", "çok", "kendi", "her"
}


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("📋 CONFIG AYARLARI")
    print(f"🏠 Proje: {PROJECT_ROOT}")
    print(f"📂 Giriş: {INPUT_DIR}")
    print(f"📂 Çıkış: {OUTPUT_DIR}")
    print(f"🤖 LLM: {LLM_MODEL}")
    print(f"🔗 Ollama: {OLLAMA_BASE_URL}")
    print(f"⚙️  Chunk Size: {CHUNK_SIZE}")
    print("✅ Config hazır")