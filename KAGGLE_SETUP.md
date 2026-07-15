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
3. **Run → Restart Session** before a clean run

## Step 2 — Add Gemma Model
1. **Add Input** → **Models**
2. Search: `gemma-4`
3. Select: **gemma-4-e2b-it** (or **gemma-4-e2b**) — Transformers
4. Click **Add**
5. Remove any **gemma-2** models

## Step 3 — Run these cells in order

### Cell 1 — Clone (always `chdir` to `/kaggle/working` first)
```python
import os, shutil, sys

os.chdir("/kaggle/working")
if os.path.exists("/kaggle/working/Judisurely"):
    shutil.rmtree("/kaggle/working/Judisurely")

!git clone https://github.com/Harsh7t/Judisurely.git /kaggle/working/Judisurely

os.chdir("/kaggle/working/Judisurely")
sys.path = [p for p in sys.path if "Judisurely" not in p]
sys.path.insert(0, "/kaggle/working/Judisurely")

assert os.path.isfile("data/legal_kb.json")
print("Ready:", os.getcwd())
```

### Cell 2 — Install (two-step to avoid pip conflict)
```python
!pip install -q -r requirements-kaggle.txt
!pip install -q "gradio==4.44.1" "gradio-client==1.3.0" --no-deps
!pip install -q aiofiles ffmpy python-multipart httpx orjson semantic-version toml typer "websockets==12.0" fastapi uvicorn starlette markupsafe packaging anyio sniffio h11 jinja2 huggingface-hub
print("Install done")
```

Ignore other Kaggle package warnings (`google-adk`, etc.).

### Cell 3 — Verify Gemma path
```python
import glob, os
os.chdir("/kaggle/working/Judisurely")
configs = glob.glob("/kaggle/input/models/**/config.json", recursive=True)
for c in configs:
    print(c)
gemma_path = configs[0].replace("/config.json", "")
assert "gemma-4" in gemma_path, f"Wrong model: {gemma_path}"
print("✅ Gemma path:", gemma_path)
```

### Cell 4 — Quick test (~3–5 min)
```python
import os, sys
os.chdir("/kaggle/working/Judisurely")
sys.path.insert(0, "/kaggle/working/Judisurely")

from utils.gemma_client import load_gemma
from utils.rag import load_knowledge_base
from utils.pipeline import analyze_notice

load_knowledge_base()
load_gemma()
sample = open("data/sample_notices/rent_notice_delhi.txt").read()
r = analyze_notice(text=sample, language="English")
print(r["reasoning"]["plain_language_summary"])
```

### Cell 5 — Launch demo
```python
import os
os.chdir("/kaggle/working/Judisurely")
!python run_kaggle.py
```
**Copy the `https://xxxxx.gradio.live` URL** for submission.

## Step 4 — Save for judges
1. **Save Version** → **Save & Run All (Commit)**
2. Visibility: **Public**
3. Attach notebook URL + Gradio URL to writeup

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ResolutionImpossible` (huggingface_hub) | Use Cell 2 two-step install (`--no-deps` for Gradio) |
| `Judisurely/Judisurely/...` path | Restart Session, then Cell 1 (never delete while cwd is inside that folder) |
| `legal_kb.json` not found | Confirm `os.getcwd()` is `/kaggle/working/Judisurely` and `data/legal_kb.json` exists |
| Wrong model (gemma-2) | Remove it; add gemma-4-e2b / e2b-it |
| CUDA OOM | Use e2b only (not 12b/26b) |
| Shell getcwd / rmtree error | `os.chdir("/kaggle/working")` then Restart Session |
