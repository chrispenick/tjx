
# TJX Style Quiz – LLM Outfit Recommender (Python + OpenAI + pytest + Streamlit)

This demo builds a **style quiz + outfit recommender** that can run in CLI or Streamlit UI mode.  
It uses T.J.Maxx product JSON-LD (when live) or fixtures (in MOCK mode).

## Features
- CLI quiz and a Streamlit web UI
- Live or MOCK fixture mode
- Caching of catalog
- Pytest suite
- OpenAI integration with stub fallback

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### CLI
```bash
python -m tjx_style_demo.main
```

### Streamlit UI
```bash
# from the project ROOT (the folder that has tjx_style_demo/ in it)
export PYTHONPATH="$PWD"          # Windows PowerShell: $env:PYTHONPATH=(Get-Location)
streamlit run tjx_style_demo/streamlit_app.py --server.fileWatcherType=none

```

Use sidebar controls to toggle MOCK mode and rebuild catalog.

Run tests:
```bash
pytest -q
```
