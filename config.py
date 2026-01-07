"""
PageGeneral - Configuration
Minimal settings for PDF extraction
"""

from pathlib import Path

# ============================================================================
# PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
PROCESSED_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Create directories
for directory in [DATA_DIR, INPUT_DIR, PROCESSED_DIR, CACHE_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# OLLAMA
# ============================================================================

OLLAMA_BASE_URL = "http://localhost:11434"
LLM_MODEL = "qwen2.5:7b"
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 500

# ============================================================================
# DIVISIONS - Updated for actual PDF content
# ============================================================================

DIVISION_LIST = [
    "5 nci Kafkas Tümeni",
    "10 ncu Kafkas Tümeni",
    "11 nci Kafkas Tümeni",
    "12 nci Tümen",
    "15 nci Tümen",
    "23 ncü Tümen",
    "24 ncü Tümen",
    "27 nd Tümen",
    "36 ncı Tümen",
    "41 nci Tümen"
]

# ============================================================================
# EXTRACTION
# ============================================================================

EXTRACTION_CONFIDENCE_THRESHOLD = 0.5
VERBOSE = True
