"""Gemma 4 model loading and inference — Kaggle + local dev mock."""

from __future__ import annotations

import glob
import json
import os
import re
from pathlib import Path
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
    return os.getenv("JUDISURELY_MODEL_PATH") or os.getenv("NYAY_MITRA_MODEL_PATH")


def is_dev_mode() -> bool:
    return os.getenv("JUDISURELY_DEV", os.getenv("NYAY_MITRA_DEV", "0")) == "1"


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


def _ensure_chat_template(tokenizer_or_processor, model_path: str) -> None:
    """Gemma 4 ships chat_template.jinja separately; older transformers miss it."""
    tmpl = getattr(tokenizer_or_processor, "chat_template", None)
    if tmpl:
        return

    # Prefer tokenizer.chat_template if this is a processor
    tok = getattr(tokenizer_or_processor, "tokenizer", None)
    if tok is not None and getattr(tok, "chat_template", None):
        tokenizer_or_processor.chat_template = tok.chat_template
        return

    jinja_paths = [
        Path(model_path) / "chat_template.jinja",
        *Path(model_path).glob("**/chat_template.jinja"),
    ]
    for jp in jinja_paths:
        if jp.is_file():
            text = jp.read_text(encoding="utf-8")
            tokenizer_or_processor.chat_template = text
            if tok is not None:
                tok.chat_template = text
            print(f"Loaded chat template from {jp}")
            return

    # Minimal Gemma-style fallback so inference still works
    fallback = (
        "{{ bos_token }}"
        "{% for message in messages %}"
        "{% if message['role'] == 'user' %}"
        "<start_of_turn>user\n{{ message['content'] }}<end_of_turn>\n"
        "{% elif message['role'] == 'model' or message['role'] == 'assistant' %}"
        "<start_of_turn>model\n{{ message['content'] }}<end_of_turn>\n"
        "{% endif %}"
        "{% endfor %}"
        "{% if add_generation_prompt %}<start_of_turn>model\n{% endif %}"
    )
    tokenizer_or_processor.chat_template = fallback
    if tok is not None:
        tok.chat_template = fallback
    print("Using fallback Gemma chat template")


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
            "Locally: set JUDISURELY_DEV=1 for mock mode."
        )

    import torch
    from transformers import AutoProcessor, AutoTokenizer, BitsAndBytesConfig
    from transformers.models.auto.configuration_auto import CONFIG_MAPPING

    if "gemma4" not in CONFIG_MAPPING:
        raise RuntimeError(
            "Your transformers version does not support Gemma 4 (model_type=gemma4). "
            "On Kaggle run:\n"
            '  !pip install -q -U "git+https://github.com/huggingface/transformers.git"\n'
            "Then Restart Session and re-run from Cell 1."
        )

    # Gemma 4 requires very recent transformers (model_type=gemma4)
    try:
        from transformers.models.auto.configuration_auto import CONFIG_MAPPING

        if "gemma4" not in CONFIG_MAPPING:
            raise RuntimeError(
                "Transformers too old for Gemma 4. On Kaggle run:\n"
                "  !pip install -q -U 'git+https://github.com/huggingface/transformers.git'\n"
                "Then Restart Session and re-run from Cell 1."
            )
    except ImportError:
        pass

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    # Prefer Gemma 4 multimodal class; fall back to CausalLM
    model_cls = None
    try:
        from transformers import AutoModelForMultimodalLM

        model_cls = AutoModelForMultimodalLM
    except ImportError:
        try:
            from transformers import AutoModelForImageTextToText

            model_cls = AutoModelForImageTextToText
        except ImportError:
            from transformers import AutoModelForCausalLM

            model_cls = AutoModelForCausalLM

    print(f"Loading Gemma from: {path}")
    print(f"Using model class: {model_cls.__name__}")

    try:
        _processor = AutoProcessor.from_pretrained(path, trust_remote_code=True)
        _ensure_chat_template(_processor, path)
        _model = model_cls.from_pretrained(
            path,
            quantization_config=bnb,
            device_map="cuda:0",
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )
        _use_tokenizer_only = False
        # Keep tokenizer reference for decoding fallbacks
        _tokenizer = getattr(_processor, "tokenizer", None) or _processor
        return _model, _processor
    except Exception as e:
        print(f"Processor load failed ({e}); falling back to tokenizer-only")
        _tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
        _ensure_chat_template(_tokenizer, path)
        from transformers import AutoModelForCausalLM

        _model = AutoModelForCausalLM.from_pretrained(
            path,
            quantization_config=bnb,
            device_map="cuda:0",
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )
        _processor = _tokenizer
        _use_tokenizer_only = True
        return _model, _tokenizer


def _get_device(model) -> Any:
    try:
        return model.device
    except Exception:
        pass
    try:
        return next(model.parameters()).device
    except Exception:
        import torch

        return torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def _build_messages(system_prompt: str, user_input: str, image=None) -> list:
    """Build chat messages. With image, use multimodal content list for Gemma 4."""
    text = f"{system_prompt}\n\n{user_input}"
    if image is not None:
        return [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": text},
                ],
            }
        ]
    return [{"role": "user", "content": text}]


def _format_prompt_fallback(system_prompt: str, user_input: str) -> str:
    return (
        f"<start_of_turn>user\n{system_prompt}\n\n{user_input}<end_of_turn>\n"
        f"<start_of_turn>model\n"
    )


def _move_inputs_to_device(out, device) -> tuple[Any, int]:
    if isinstance(out, dict) or hasattr(out, "keys"):
        inputs = {k: v.to(device) if hasattr(v, "to") else v for k, v in dict(out).items()}
        return inputs, int(inputs["input_ids"].shape[-1])
    inputs = out.to(device)
    return inputs, int(inputs.shape[-1])


def _eos_pad_ids(tok) -> dict:
    kwargs = {}
    eos = getattr(tok, "eos_token_id", None)
    pad = getattr(tok, "pad_token_id", None)
    if eos is not None:
        kwargs["eos_token_id"] = eos
    if pad is not None:
        kwargs["pad_token_id"] = pad
    elif eos is not None:
        kwargs["pad_token_id"] = eos
    return kwargs


def call_gemma(
    system_prompt: str,
    user_input: str,
    max_tokens: int = 768,
    temperature: float = 0.3,
    image=None,
) -> str:
    """Run a single Gemma generation call. Optional PIL image for multimodal extract."""
    global _model, _processor, _tokenizer
    import time

    if is_dev_mode():
        return _mock_response(system_prompt, user_input)

    if _model is None:
        load_gemma()

    if _model is None:
        raise RuntimeError(
            "Gemma model not loaded. Add gemma-4-e2b-it on Kaggle or set JUDISURELY_DEV=1 locally."
        )

    import torch

    model = _model
    proc = _processor
    tok = _tokenizer or getattr(proc, "tokenizer", None) or proc
    device = _get_device(model)
    messages = _build_messages(system_prompt, user_input, image=image)

    # Ensure template exists before calling
    path = find_model_path() or ""
    _ensure_chat_template(proc, path)
    if tok is not proc:
        _ensure_chat_template(tok, path)

    inputs = None
    input_len = 0
    t0 = time.time()
    print(f"[gemma] starting generate (image={image is not None}, max_new={max_tokens})...")

    # Strategy 1: processor.apply_chat_template (Gemma 4 multimodal + text)
    try:
        out = proc.apply_chat_template(
            messages,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            add_generation_prompt=True,
            enable_thinking=False,
        )
        inputs, input_len = _move_inputs_to_device(out, device)
    except Exception as e1:
        print(f"apply_chat_template via processor failed: {e1}")
        # Drop image and retry text-only if multimodal template failed
        text_messages = _build_messages(system_prompt, user_input, image=None)
        try:
            out = tok.apply_chat_template(
                text_messages,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
                add_generation_prompt=True,
            )
            inputs, input_len = _move_inputs_to_device(out, device)
        except Exception as e2:
            print(f"tokenizer chat template failed: {e2}; using string fallback")
            prompt = _format_prompt_fallback(system_prompt, user_input)
            encoded = tok(prompt, return_tensors="pt")
            inputs = {k: v.to(device) for k, v in encoded.items()}
            input_len = int(inputs["input_ids"].shape[-1])

    # Cap tokens so share links don't sit past ~5 min on 3 calls
    max_tokens = min(int(max_tokens), 1024)
    gen_kwargs = {
        "max_new_tokens": max_tokens,
        "do_sample": temperature > 0,
        **_eos_pad_ids(tok),
    }
    if temperature > 0:
        gen_kwargs["temperature"] = temperature

    with torch.inference_mode():
        if isinstance(inputs, dict):
            outputs = model.generate(**inputs, **gen_kwargs)
        else:
            outputs = model.generate(inputs, **gen_kwargs)

    generated = outputs[0][input_len:]
    try:
        text = proc.decode(generated, skip_special_tokens=True)
    except Exception:
        text = tok.decode(generated, skip_special_tokens=True)

    # If thinking tags remain, keep content after model turn / strip think blocks
    if "<|channel|>" in text or "<|think|>" in text:
        for marker in ("</think>", "<end_of_thought>", "<|channel|>final"):
            if marker in text:
                text = text.split(marker)[-1]
                break

    print(f"[gemma] done in {time.time() - t0:.1f}s ({len(text)} chars)")
    return text.strip()


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
