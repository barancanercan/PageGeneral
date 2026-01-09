<p align="center">
  <h1 align="center">PageGeneral</h1>
  <p align="center">
    <strong>Historical Document Intelligence</strong><br>
    Extract structured information from Turkish military historical PDFs using Local LLM
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/LLM-Qwen2.5--7B-green.svg" alt="LLM">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
  <img src="https://img.shields.io/badge/status-v1.0-brightgreen.svg" alt="Status">
</p>

---

## Overview

PageGeneral is a specialized NLP pipeline for extracting military division information from historical Turkish documents. It combines traditional regex pre-filtering with modern LLM capabilities to achieve high accuracy while running entirely on local hardware.

### Key Features

| Feature | Description |
|---------|-------------|
| **Local LLM** | Runs on CPU/GPU without API costs (Qwen2.5-7B) |
| **Hybrid Extraction** | Regex pre-filter + LLM verification |
| **Page Tracking** | Accurate source page numbers for citations |
| **Dynamic Confidence** | 0.0-1.0 scoring based on match quality |
| **Turkish Optimized** | Handles Turkish characters and military terminology |

---

## How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   PDF       │────▶│   Parser    │────▶│   Regex     │────▶│    LLM      │
│   Input     │     │  (pypdf)    │     │  Pre-filter │     │  (Qwen2.5)  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                   │                    │
                           ▼                   ▼                    ▼
                    Paragraphs with      Candidate          Structured JSON
                    page numbers         paragraphs         with confidence
```

---

## Installation

### Prerequisites

- Python 3.11+
- 16GB RAM (recommended for LLM)
- ~15GB disk space (for model weights)

### Setup

```bash
# Clone repository
git clone https://github.com/barancanercan/PageGeneral.git
cd PageGeneral

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Set HuggingFace token (optional, for gated models)
echo "HF_TOKEN=your_token_here" > .env
```

---

## Quick Start

### 1. Add PDF Files

```bash
cp your_document.pdf data/input/
```

### 2. Configure Target Divisions

Edit `config.py`:

```python
DIVISION_LIST = [
    "5 nci Kafkas Tümeni",
    "15 nci Tümen",
    "36 ncı Tümen",
    # Add more...
]
```

### 3. Run Extraction

```bash
python scripts/extract.py
```

### 4. Check Results

```bash
cat output/extractions_*.json
```

---

## Output Format

```json
{
  "id": "parag_142",
  "embedding": [],
  "document": "Azerbaycan'daki 15 nci Tümen, 5 nci Kafkas Tümeni ve 36 ncı Tümen'den...",
  "metadata": {
    "division": ["15. Tümen", "5. Kafkas Tümeni", "36. Tümen"],
    "confidence": 1.0,
    "source_page": 241
  },
  "book": "Turk_istiklal_harbi",
  "timestamp": "2024-01-09T13:31:00"
}
```

### Confidence Scoring

| Score | Interpretation |
|-------|----------------|
| **1.0** | Division name found exactly as specified |
| **0.8-0.9** | Division number matches, format slightly different |
| **0.6-0.7** | Indirect or contextual reference |
| **0.0** | No division detected |

---

## Project Structure

```
PageGeneral/
├── config.py                 # Configuration & division list
├── requirements.txt          # Python dependencies
├── scripts/
│   └── extract.py            # Main extraction script
├── src/
│   ├── __init__.py
│   ├── pdf_parser.py         # PDF → paragraphs with page info
│   ├── llm.py                # Qwen2.5 local inference
│   └── division_extractor.py # Hybrid extraction logic
├── tests/
│   └── test_2pages.py        # Page-range test script
├── data/
│   ├── input/                # Place PDFs here
│   └── processed/            # Cached markdown files
├── output/                   # JSON extraction results
└── docs/
    └── V2_ROADMAP.md         # Future development plans
```

---

## Configuration Reference

| Parameter | Default | Description |
|-----------|---------|-------------|
| `HF_MODEL` | `Qwen/Qwen2.5-7B-Instruct` | HuggingFace model ID |
| `LLM_TEMPERATURE` | `0.1` | Lower = more deterministic |
| `LLM_MAX_TOKENS` | `500` | Max response length |
| `EXTRACTION_CONFIDENCE_THRESHOLD` | `0.5` | Minimum confidence to include |
| `VERBOSE` | `True` | Print progress messages |

---

## Testing

```bash
# Test with specific page range
python tests/test_2pages.py

# Check output
cat output/test_2pages_output.json
```

---

## Performance

| Metric | Value |
|--------|-------|
| PDF Parse Speed | ~1 sec / 100 pages |
| LLM Inference | ~10 sec / paragraph (CPU) |
| Memory Usage | ~8-12 GB |
| Accuracy | High (with proper division list) |

---

## Roadmap

### v1.0 (Current)
- [x] PDF parsing with page tracking
- [x] Regex + LLM hybrid extraction
- [x] Dynamic confidence scoring
- [x] JSON output format

### v2.0 (Planned)
- [ ] Vector database integration (ChromaDB)
- [ ] Multi-book search
- [ ] Gradio web interface
- [ ] Custom query support
- [ ] CSV/Markdown export

See [V2_ROADMAP.md](docs/V2_ROADMAP.md) for detailed plans.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| PDF Parsing | pypdf |
| LLM | Qwen2.5-7B-Instruct |
| ML Framework | PyTorch + Transformers |
| Language | Python 3.11 |

---

## Contributing

Contributions are welcome! Please read the roadmap first to understand the project direction.

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and test
python tests/test_2pages.py

# Commit and push
git commit -m "feat: your feature description"
git push origin feature/your-feature
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [Qwen2.5](https://huggingface.co/Qwen) - Alibaba's open LLM
- Turkish General Staff Military History Archives
- HuggingFace Transformers team

---

<p align="center">
  <sub>Built with passion for historical research</sub>
</p>
