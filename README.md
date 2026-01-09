# PageGeneral

Turkish Military Division Extraction from Historical PDFs using Local LLM (Qwen2.5-7B).

## Project Structure

```
PageGeneral/
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── scripts/
│   └── extract.py         # Main extraction script
├── src/
│   ├── pdf_parser.py      # PDF to text
│   ├── llm.py             # Qwen2.5 local client
│   └── division_extractor.py
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

## Output Format

```json
{
  "id": "parag_5",
  "embedding": [],
  "document": "Full paragraph text",
  "metadata": {
    "division": ["5 nci Kafkas Tümeni", "10 ncu Kafkas Tümeni"],
    "confidence": 0.95,
    "source_page": 5
  }
}
```

## Configuration

Edit `config.py` to modify:
- `DIVISION_LIST`: Target divisions to extract
- `LLM_TEMPERATURE`: Model temperature (default: 0.1)
- `LLM_MAX_TOKENS`: Max response tokens (default: 500)