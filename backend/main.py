"""Judisurely FastAPI backend."""

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from utils.gemma_client import load_gemma  # noqa: E402
from utils.pdf_generator import generate_pdf  # noqa: E402
from utils.pipeline import analyze_notice  # noqa: E402
from utils.rag import load_knowledge_base  # noqa: E402
from utils.schemas import TEMPLATE_NAMES  # noqa: E402

app = FastAPI(
    title="Judisurely API",
    description="AI Legal Action Engine — Gemma 4 + RAG",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    load_knowledge_base()
    try:
        load_gemma()
    except Exception as e:
        print(f"Gemma load skipped (dev/mock): {e}")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "Judisurely",
        "dev_mode": os.getenv("JUDISURELY_DEV", os.getenv("NYAY_MITRA_DEV", "0")) == "1",
        "templates": TEMPLATE_NAMES,
    }


@app.post("/api/analyze")
async def analyze(
    text: str = Form(""),
    language: str = Form("English"),
    template_key: str = Form("legal_reply"),
    file: Optional[UploadFile] = File(None),
):
    file_path = None
    if file and file.filename:
        suffix = Path(file.filename).suffix or ".txt"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            file_path = tmp.name

    result = analyze_notice(
        text=text,
        file_path=file_path,
        language=language,
        template_key=template_key,
    )
    return result


@app.post("/api/pdf")
async def create_pdf(draft_text: str = Form(...)):
    path = generate_pdf(draft_text)
    return FileResponse(path, filename="judisurely_draft.pdf", media_type="application/pdf")
