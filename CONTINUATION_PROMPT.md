# Nyay Mitra — Continuation Prompt for Cursor

Copy everything below into a new Cursor chat to continue this project.

---

## PROJECT: Nyay Mitra — AI Legal Action Engine
**Hackathon:** Build with Gemma – AIMS DTU | Track 1: AI for Legal Assistance
**Team:** Harshit, Prem, Shreya
**Deadline:** Jul 15, 2026, 5:00 PM IST

## REPO LOCATION
`/Users/harshitsengar/Desktop/GemmaTRACK1`

## WHAT'S DONE
1. **Dataset:** `data/legal_kb.json` (55 Indian law clauses), `data/sample_notices/` (6 test notices), `data/draft_templates.json`
2. **AI Pipeline:** `utils/pipeline.py` — 3 Gemma calls (extract → RAG → reason → draft) + `utils/rag.py` (TF-IDF), `utils/gemma_client.py`, `utils/pdf_generator.py`
3. **Gradio demo:** `utils/gradio_app.py` + `run.py` (works locally with `NYAY_MITRA_DEV=1`)
4. **FastAPI backend:** `backend/main.py` — `/api/analyze`, `/api/pdf`, `/api/health`
5. **Next.js frontend:** `frontend/` — full UI with upload, tabs (summary/actions/draft/sources), deadline countdown, thinking mode, case history (localStorage), PDF download
6. **Docker:** `docker-compose.yml` for backend + frontend
7. **Kaggle:** Gemma 4 e2b-it loads at `/kaggle/input/models/google/gemma-4/transformers/gemma-4-e2b-it/1`

## ARCHITECTURE
```
User → Next.js (port 3000) → FastAPI (port 8000) → Gemma 4 + RAG (legal_kb.json)
Alternative: Gradio in Kaggle notebook for hackathon submission demo
```

## HOW TO RUN LOCALLY
```bash
# Terminal 1 — Backend
cd /Users/harshitsengar/Desktop/GemmaTRACK1
source venv/bin/activate
pip install -r requirements-local.txt
export NYAY_MITRA_DEV=1
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

## HOW TO RUN ON KAGGLE (REAL GEMMA)
1. GPU T4, Internet ON, Add Gemma 4 e2b-it model
2. Clone GitHub repo
3. Load Gemma into `utils.gemma_client` globals
4. Either run Gradio (`python run.py`) OR FastAPI + use Gradio share URL for submission

## SUBMISSION STILL NEEDED
- [ ] Push to public GitHub
- [ ] Kaggle notebook public + Save & Run All
- [ ] Gradio `share=True` demo URL OR deployed website URL
- [ ] Kaggle Writeup ≤1500 words (problem, Gemma usage, architecture, impact)
- [ ] Attach GitHub + demo links to writeup

## WHAT TO BUILD NEXT (priority order)
1. **Deploy:** Frontend on Vercel (`NEXT_PUBLIC_API_URL`), Backend on Railway/Render
2. **Kaggle integration:** Wire real Gemma (not mock) in notebook, test end-to-end with sample notices
3. **Image upload:** Gemma multimodal for notice images (currently OCR fallback)
4. **Writeup + screenshots** for submission
5. **Polish:** Hindi UI labels, voice input (STT), offline toggle mockup
6. **Tests:** Run 5 sample notices, document accuracy metrics for writeup

## KEY FILES
- Pipeline: `utils/pipeline.py`
- API: `backend/main.py`
- Frontend: `frontend/app/page.tsx`, `frontend/components/`
- Prompts: `utils/schemas.py`
- RAG: `utils/rag.py` + `data/legal_kb.json`

## GEMMA INTEGRATION (30% of score — emphasize in writeup)
1. **Call 1:** Extraction — notice → structured JSON
2. **RAG:** TF-IDF over 55 curated clauses (anti-hallucination)
3. **Call 2:** Reasoning — rights, options, action steps + thinking trace
4. **Call 3:** Draft generation — auto-filled legal letter

## ONE-LINE PITCH
"Every other tool answers 'what does this mean?' Nyay Mitra answers 'what do I do now?' — and hands you the document to do it with."

## INSTRUCTION FOR CURSOR
Read the codebase at `/Users/harshitsengar/Desktop/GemmaTRACK1`. Continue from where we left off. Priority: get Kaggle demo working with real Gemma, deploy website, and help write the Kaggle submission writeup. Do not rebuild from scratch — extend existing code.
