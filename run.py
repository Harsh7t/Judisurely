#!/usr/bin/env python3
"""Entry point: python run.py"""

from utils.gemma_client import load_gemma
from utils.rag import load_knowledge_base
from utils.gradio_app import launch

if __name__ == "__main__":
    print("Loading legal knowledge base...")
    load_knowledge_base()
    print("Loading Gemma (or mock mode if JUDISURELY_DEV=1)...")
    load_gemma()
    print("Launching Judisurely...")
    print("Launching Judisurely at http://127.0.0.1:7860")
    launch(share=False)
