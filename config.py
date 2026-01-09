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
CACHE_DIR = DATA_DIR / "cache"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Create directories
for directory in [DATA_DIR, INPUT_DIR, PROCESSED_DIR, CACHE_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# HUGGINGFACE API
# ============================================================================

HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_MODEL = "Qwen/Qwen2.5-7B-Instruct"

# LLM settings
LLM_TEMPERATURE = 0.1  # Düşük = daha deterministik
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