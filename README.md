# PageGeneral

Turkish Military Division Extraction from Historical PDFs using Local LLM (Qwen2.5-7B).

## Features

- PDF parsing with page-level paragraph extraction
- Regex pre-filtering + LLM hybrid extraction
- Dynamic confidence scoring (0.0-1.0)
- Accurate PDF page number tracking

## Project Structure

```
PageGeneral/
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── scripts/
│   └── extract.py         # Main extraction script
├── src/
│   ├── pdf_parser.py      # PDF to text with page info
│   ├── llm.py             # Qwen2.5 local client
│   └── division_extractor.py
├── tests/
│   └── test_2pages.py     # Test script
├── data/
│   ├── input/             # Place PDFs here
│   └── processed/         # Markdown outputs
└── output/                # JSON extraction results
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

1. Place PDF files in `data/input/`
2. Run extraction:

```bash
python scripts/extract.py
```

3. Test with specific pages:

```bash
python tests/test_2pages.py
```

## Output Format

```json
{
  "id": "parag_5",
  "embedding": [],
  "document": "Full paragraph text",
  "metadata": {
    "division": ["15. Tümen", "5. Kafkas Tümeni"],
    "confidence": 1.0,
    "source_page": 241
  }
}
```

### Confidence Scoring

| Score | Meaning |
|-------|---------|
| 1.0 | Division name explicitly found |
| 0.8-0.9 | Division number found, format differs |
| 0.6-0.7 | Indirect reference |
| 0.0 | No division found |

## Configuration

Edit `config.py` to modify:
- `DIVISION_LIST`: Target divisions to extract
- `LLM_TEMPERATURE`: Model temperature (default: 0.1)
- `LLM_MAX_TOKENS`: Max response tokens (default: 500)