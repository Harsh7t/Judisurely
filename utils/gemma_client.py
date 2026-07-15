"""Gemma 4 model loading and inference — Kaggle + local dev mock."""

from __future__ import annotations

import glob
import json
import os
import re
from typing import Any, Optional

# Globals cached after first load
_model = None
_processor = None
_tokenizer = None
_use_tokenizer_only = False


def find_model_path() -> Optional[str]:
    """Auto-detect Gemma path on Kaggle."""
    configs = glob.glob("/kaggle/input/models/**/config.json", recursive=True)
    if configs:
        return configs[0].replace("/config.json", "")
    legacy = glob.glob("/kaggle/input/gemma-4/**/config.json", recursive=True)
    if legacy:
        return legacy[0].replace("/config.json", "")
    return os.getenv("NYAY_MITRA_MODEL_PATH")


def is_dev_mode() -> bool:
    return os.getenv("NYAY_MITRA_DEV", "0") == "1"


def parse_json_from_response(text: str) -> dict:
    """Extract JSON from Gemma response, handling markdown fences."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fence:
        text = fence.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    return json.loads(text)


def load_gemma(model_path: Optional[str] = None, force_reload: bool = False):
    """Load Gemma model and processor/tokenizer once."""
    global _model, _processor, _tokenizer, _use_tokenizer_only

    if _model is not None and not force_reload:
        return _model, _processor or _tokenizer

    if is_dev_mode():
        return None, None

    path = model_path or find_model_path()
    if not path:
        raise RuntimeError(
            "No Gemma model found. On Kaggle: Add Input → Models → gemma-4-e2b-it. "
            "Locally: set NYAY_MITRA_DEV=1 for mock mode."
        )

    import torch
    from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer, BitsAndBytesConfig

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    try:
        _processor = AutoProcessor.from_pretrained(path)
        _model = AutoModelForCausalLM.from_pretrained(
            path,
            quantization_config=bnb,
            device_map="cuda:0",
            torch_dtype=torch.bfloat16,
        )
        _use_tokenizer_only = False
        return _model, _processor
    except Exception:
        _tokenizer = AutoTokenizer.from_pretrained(path)
        _model = AutoModelForCausalLM.from_pretrained(
            path,
            quantization_config=bnb,
            device_map="cuda:0",
            torch_dtype=torch.bfloat16,
        )
        _processor = _tokenizer
        _use_tokenizer_only = True
        return _model, _tokenizer


def call_gemma(
    system_prompt: str,
    user_input: str,
    max_tokens: int = 1536,
    temperature: float = 0.3,
) -> str:
    """Run a single Gemma generation call."""
    global _model, _processor

    if is_dev_mode():
        return _mock_response(system_prompt, user_input)

    if _model is None:
        load_gemma()

    if _model is None:
        raise RuntimeError("Gemma model not loaded. Add gemma-4-e2b-it on Kaggle or set NYAY_MITRA_DEV=1 locally.")

    import torch

    model, proc = _model, _processor
    messages = [
        {"role": "user", "content": f"{system_prompt}\n\n{user_input}"},
    ]

    if _use_tokenizer_only:
        inputs = proc.apply_chat_template(
            messages, return_tensors="pt", add_generation_prompt=True
        ).to(model.device)
        input_len = inputs.shape[-1]
        outputs = model.generate(
            inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
        )
        return proc.decode(outputs[0][input_len:], skip_special_tokens=True)

    inputs = proc.apply_chat_template(
        messages, return_tensors="pt", add_generation_prompt=True
    ).to(model.device)
    input_len = inputs.shape[-1]
    outputs = model.generate(
        inputs,
        max_new_tokens=max_tokens,
        temperature=temperature,
        do_sample=temperature > 0,
    )
    return proc.decode(outputs[0][input_len:], skip_special_tokens=True)


def _mock_response(system_prompt: str, user_input: str) -> str:
    """Deterministic mock for local UI testing without GPU."""
    if "Extract structured" in system_prompt or "document analyzer" in system_prompt:
        return json.dumps({
            "document_type": "rent_notice",
            "sender_name": "Mr. Ashok Sharma",
            "sender_role": "landlord",
            "recipient_name": "Mr. Rahul Verma",
            "date_issued": "01/07/2026",
            "deadline_date": "31/07/2026",
            "legal_sections_cited": ["Section 14(1)(e) of Delhi Rent Control Act, 1958"],
            "key_demands": ["Vacate premises by 31/07/2026"],
            "language_detected": "english",
            "summary_one_line": "Landlord demands tenant vacate for own occupation by 31 July 2026.",
        })
    if "legal reasoning" in system_prompt.lower():
        return json.dumps({
            "plain_language_summary": (
                "Your landlord has sent a notice asking you to leave the flat by 31 July 2026 "
                "claiming they need it for their own use. You have legal rights and do not have to "
                "leave immediately without proper legal process."
            ),
            "urgency_level": "HIGH",
            "urgency_reason": "Deadline is less than 30 days away.",
            "your_rights": [
                {
                    "right": "Landlord must follow due process through Rent Controller for eviction.",
                    "source": "Delhi Rent Control Act, Section 6",
                },
                {
                    "right": "Eviction for own use requires genuine need and proper notice.",
                    "source": "Delhi Rent Control Act, Section 14(1)(e)",
                },
            ],
            "your_options": [
                {"option": "Send written reply disputing the notice", "pros": "Preserves your legal position", "cons": "May escalate dispute"},
                {"option": "Approach Rent Controller", "pros": "Official legal remedy", "cons": "Takes time"},
            ],
            "action_steps": [
                {
                    "step": 1,
                    "action": "Send written acknowledgment and reply to landlord",
                    "where": "Via registered post to landlord address",
                    "deadline": "Within 7 days",
                    "documents_needed": "Notice copy, rent agreement, rent receipts",
                },
                {
                    "step": 2,
                    "action": "File objection with Rent Controller if needed",
                    "where": "Rent Controller, Delhi",
                    "deadline": "Before deadline in notice",
                    "documents_needed": "Reply copy, tenancy proof, identity proof",
                },
            ],
            "thinking_trace": "Notice cites DRC Act 14(1)(e). Retrieved clauses confirm due process required. Deadline within 30 days = HIGH urgency.",
        })
    return (
        "To,\nMr. Ashok Sharma\n\nFrom,\nMr. Rahul Verma\n\nDate: 15/07/2026\n\n"
        "Subject: Reply to your legal notice dated 01/07/2026\n\n"
        "I acknowledge receipt of your notice. I dispute the grounds stated and reserve all my rights "
        "under the Delhi Rent Control Act, 1958.\n\n"
        "This reply is sent without prejudice to my rights and contentions.\n\n"
        "Yours faithfully,\nMr. Rahul Verma"
    )
