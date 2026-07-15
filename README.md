# Nyay Mitra — AI Legal Action Engine

**Track 1: AI for Legal Assistance** | Build with Gemma – AIMS DTU

## Quick Links
- **Kaggle setup:** See [KAGGLE_SETUP.md](KAGGLE_SETUP.md)
- **Continue development:** See [CONTINUATION_PROMPT.md](CONTINUATION_PROMPT.md)

## Run on Kaggle (submission demo — real Gemma 4)

1. Push this repo to public GitHub
2. Create Kaggle notebook → GPU T4 → Internet ON
3. Add model: `google/gemma-4` → `gemma-4-e2b-it`
4. Open `nyay_mitra.ipynb` or follow KAGGLE_SETUP.md
5. Replace `YOUR_USERNAME` in clone cell
6. Run all cells → copy `gradio.live` URL
7. Save Version → Public

```python
!git clone https://github.com/YOUR_USERNAME/nyay-mitra.git
%cd nyay-mitra
!pip install -q -r requirements-kaggle.txt
!python run_kaggle.py
```

## Run locally (mock mode — no GPU)

```bash
# Backend
source venv/bin/activate
pip install -r requirements-local.txt
export NYAY_MITRA_DEV=1
uvicorn backend.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend && npm install && npm run dev
# → http://localhost:3000
```

## Project Structure

```
├── run_kaggle.py          # Kaggle entry point (real Gemma + Gradio)
├── nyay_mitra.ipynb       # Kaggle notebook
├── utils/                 # Pipeline, RAG, Gemma client, Gradio
├── data/legal_kb.json     # 55 curated legal clauses
├── backend/               # FastAPI API
├── frontend/              # Next.js website
└── requirements-kaggle.txt
```

## Gemma Integration (3 calls)

1. **Extract** — notice → structured JSON
2. **Reason** — facts + RAG clauses → rights, options, action steps
3. **Draft** — auto-filled legal letter

## Team

Harshit, Prem, Shreya
