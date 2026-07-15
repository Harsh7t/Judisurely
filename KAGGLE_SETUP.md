# Nyay Mitra — Kaggle Setup (Step by Step)

## Before you start
- [ ] Code pushed to **public GitHub**
- [ ] Kaggle competition joined: Build with Gemma – AIMS DTU

---

## Step 1 — Create Kaggle Notebook
1. Go to competition → **Code** → **New Notebook**
2. **Settings** (right sidebar):
   - Accelerator: **GPU T4 x2**
   - Internet: **ON**
   - Persistence: Files only

## Step 2 — Add Gemma Model
1. **Add Input** → **Models**
2. Search: `gemma-4`
3. Select: **gemma-4-e2b-it** (Transformers, V1)
4. Click **Add**

## Step 3 — Run notebook cells (copy from `nyay_mitra.ipynb`)

### Cell 1 — Clone repo FIRST (requirements file is inside the repo)
```python
!git clone https://github.com/Harsh7t/Judisurely.git
%cd Judisurely
import sys; sys.path.insert(0, ".")
print("Ready!")
```

### Cell 2 — Install dependencies
```python
# Warnings about pydantic/websockets vs Kaggle pre-installed packages are OK — ignore them
!pip install -q -r requirements-kaggle.txt
```
**Do NOT run `pip install -U transformers` separately** — it breaks Gradio's huggingface_hub pin.

### Cell 3 — Verify Gemma path
```python
import glob
configs = glob.glob("/kaggle/input/models/**/config.json", recursive=True)
assert configs, "Add Gemma 4 e2b-it model!"
print("Gemma:", configs[0].replace("/config.json", ""))
```

### Cell 4 — Quick test (optional, ~2 min)
```python
from utils.pipeline import analyze_notice
from utils.gemma_client import load_gemma
from utils.rag import load_knowledge_base

load_knowledge_base()
load_gemma()
sample = open("data/sample_notices/rent_notice_delhi.txt").read()
r = analyze_notice(text=sample, language="English")
print(r["reasoning"]["urgency_level"])
print(r["reasoning"]["plain_language_summary"][:200])
```

### Cell 5 — Launch demo (submission URL)
```python
!python run_kaggle.py
```
**Copy the `https://xxxxx.gradio.live` URL** — this is your live demo link.

## Step 4 — Save for judges
1. **Save Version** → **Save & Run All (Commit)**
2. Set visibility: **Public**
3. Attach notebook URL + Gradio URL to writeup

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Model not found | Add Input → Models → gemma-4-e2b-it |
| CUDA OOM | Use e2b-it (not 12b), 4-bit already enabled |
| Mock/fake output | Do NOT set NYAY_MITRA_DEV on Kaggle |
| JSON parse error | Gemma sometimes wraps JSON in ``` — pipeline has fallback |
| Gradio URL expired | Re-run cell 5 before judges review (72h limit) |

---

## What judges see with real Gemma
- Notice-specific extraction (not canned mock)
- Grounded citations from legal_kb.json
- Custom draft letter with real names/dates
- Thinking trace from actual Gemma reasoning
