#!/usr/bin/env python3
"""
Kaggle entry point — loads Gemma 4 + RAG + launches Gradio demo.
Do NOT set NYAY_MITRA_DEV=1 on Kaggle.
"""

import os

# Ensure real Gemma is used on Kaggle
os.environ.pop("NYAY_MITRA_DEV", None)


def main():
    # Must run before Gradio import (HfFolder removed in new huggingface_hub)
    from utils.hf_compat import patch_huggingface_hub_for_gradio

    patch_huggingface_hub_for_gradio()

    from utils.gemma_client import find_model_path, load_gemma
    from utils.rag import load_knowledge_base
    from utils.gradio_app import launch

    print("=" * 50)
    print("Nyay Mitra — Kaggle Demo")
    print("=" * 50)

    path = find_model_path()
    if not path:
        raise RuntimeError(
            "Gemma not found! Add Input → Models → google/gemma-4 → gemma-4-e2b-it"
        )
    print(f"Gemma path: {path}")

    print("Loading legal knowledge base...")
    kb = load_knowledge_base()
    print(f"  → {len(kb)} legal clauses loaded")

    print("Loading Gemma 4 (4-bit, ~3-5 min)...")
    load_gemma(path)
    print("  → Gemma ready on GPU")

    print("\nLaunching Gradio demo...")
    print("COPY the gradio.live URL for your submission!\n")
    launch(share=True)


if __name__ == "__main__":
    main()
