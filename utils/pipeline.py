"""Nyay Mitra pipeline: Gemma extraction → RAG → reasoning → draft."""

from __future__ import annotations

import json
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional


from utils.gemma_client import call_gemma, load_gemma, parse_json_from_response
from utils.rag import format_clauses_for_prompt, load_knowledge_base, retrieve_relevant_laws
from utils.schemas import (
    DISCLAIMER,
    DRAFT_SYSTEM_PROMPT,
    EXTRACTION_SYSTEM_PROMPT,
    REASONING_SYSTEM_PROMPT,
    TEMPLATE_NAMES,
)


def _extract_text_from_file(file_path: Optional[str]) -> str:
    """Extract text from PDF or image file."""
    if not file_path:
        return ""

    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        try:
            import fitz

            doc = fitz.open(path)
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
            if text.strip():
                return text.strip()
        except Exception:
            pass

    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
        try:
            from PIL import Image
            import pytesseract

            img = Image.open(path)
            text = pytesseract.image_to_string(img)
            if text.strip():
                return text.strip()
        except Exception:
            pass

    if suffix == ".txt":
        return path.read_text(encoding="utf-8").strip()

    return ""


def _default_extraction(notice_text: str) -> dict:
    """Fallback extraction if JSON parse fails."""
    return {
        "document_type": "other",
        "sender_name": "Unknown",
        "sender_role": "other",
        "recipient_name": "Unknown",
        "date_issued": "Unknown",
        "deadline_date": None,
        "legal_sections_cited": [],
        "key_demands": [],
        "language_detected": "english",
        "summary_one_line": notice_text[:200] if notice_text else "Legal notice received",
    }


def _default_reasoning(extracted: dict, language: str) -> dict:
    """Fallback reasoning if JSON parse fails."""
    return {
        "plain_language_summary": extracted.get("summary_one_line", "Unable to parse full analysis."),
        "urgency_level": "MEDIUM",
        "urgency_reason": "Please review deadlines in the notice carefully.",
        "your_rights": [{"right": "You have the right to seek legal counsel.", "source": "General legal practice"}],
        "your_options": [{"option": "Consult a lawyer", "pros": "Professional guidance", "cons": "May involve cost"}],
        "action_steps": [
            {
                "step": 1,
                "action": "Do not ignore the notice",
                "where": "Consult lawyer or legal aid cell",
                "deadline": "As soon as possible",
                "documents_needed": "Original notice, supporting documents",
            }
        ],
        "thinking_trace": "Fallback response — JSON parsing failed. Please retry or consult a lawyer.",
    }


def analyze_notice(
    image=None,
    text: str = "",
    file_path: Optional[str] = None,
    language: str = "English",
    template_key: str = "legal_reply",
) -> dict:
    """
    Full pipeline: extract → RAG → reason → draft.
    Returns dict with all formatted outputs for Gradio.
    """
    load_knowledge_base()
    load_gemma()

    notice_text = (text or "").strip()

    if file_path:
        notice_text = notice_text or _extract_text_from_file(file_path)

    if image is not None and not notice_text:
        try:
            import pytesseract
            from PIL import Image

            if isinstance(image, str):
                img = Image.open(image)
            elif hasattr(image, "read"):
                img = Image.open(BytesIO(image.read()))
            else:
                img = image
            notice_text = pytesseract.image_to_string(img).strip()
        except Exception:
            notice_text = "[Image uploaded — OCR unavailable. Please paste notice text.]"

    if not notice_text:
        return {"error": "Please upload a file, image, or paste notice text."}

    # --- GEMMA CALL 1: Extraction ---
    extracted_raw = call_gemma(
        EXTRACTION_SYSTEM_PROMPT,
        f"Legal notice to analyze:\n\n{notice_text}",
        max_tokens=768,
        temperature=0.2,
    )
    try:
        extracted = parse_json_from_response(extracted_raw)
    except (json.JSONDecodeError, ValueError):
        extracted = _default_extraction(notice_text)

    # --- RAG retrieval (not Gemma) ---
    clauses = retrieve_relevant_laws(extracted, top_k=5)
    clauses_text = format_clauses_for_prompt(clauses)

    # --- GEMMA CALL 2: Reasoning + roadmap ---
    reasoning_prompt = REASONING_SYSTEM_PROMPT.replace("{language}", language)
    reasoning_input = f"""EXTRACTED FACTS:
{json.dumps(extracted, indent=2)}

RETRIEVED LEGAL CLAUSES (verified database):
{clauses_text}

ORIGINAL NOTICE (excerpt):
{notice_text[:3000]}
"""
    reasoning_raw = call_gemma(reasoning_prompt, reasoning_input, max_tokens=1536, temperature=0.3)
    try:
        reasoning = parse_json_from_response(reasoning_raw)
    except (json.JSONDecodeError, ValueError):
        reasoning = _default_reasoning(extracted, language)

    # --- GEMMA CALL 3: Draft generation ---
    template_name = TEMPLATE_NAMES.get(template_key, "Legal Reply")
    draft_prompt = DRAFT_SYSTEM_PROMPT.replace("{template_name}", template_name).replace(
        "{language}", language
    )
    draft_input = f"""Extracted information:
{json.dumps(extracted, indent=2)}

Legal context:
{clauses_text}

Analysis:
{json.dumps(reasoning, indent=2)}
"""
    draft_text = call_gemma(draft_prompt, draft_input, max_tokens=1024, temperature=0.4)

    return _format_outputs(extracted, reasoning, draft_text, clauses)


def _format_outputs(extracted: dict, reasoning: dict, draft_text: str, clauses: list) -> dict:
    """Format pipeline results for Gradio tabs."""
    urgency = reasoning.get("urgency_level", "MEDIUM")
    urgency_icons = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
    icon = urgency_icons.get(urgency, "⚪")

    deadline = extracted.get("deadline_date") or "Not specified"
    countdown = ""
    if deadline and deadline not in ("null", "Unknown", None):
        try:
            dl = datetime.strptime(deadline, "%d/%m/%Y")
            days_left = (dl - datetime.now()).days
            if days_left >= 0:
                countdown = f"\n\n⏱ **{days_left} days remaining** to respond."
        except ValueError:
            pass

    summary_md = f"""### 📄 {extracted.get('document_type', 'Legal Notice').replace('_', ' ').title()}

**From:** {extracted.get('sender_name', 'Unknown')} ({extracted.get('sender_role', '')})
**To:** {extracted.get('recipient_name', 'You')}
**Date issued:** {extracted.get('date_issued', 'Unknown')}
**Deadline:** {deadline}

---

{reasoning.get('plain_language_summary', '')}

{DISCLAIMER}"""

    urgency_md = f"""### {icon} Urgency: **{urgency}**

{reasoning.get('urgency_reason', '')}{countdown}

{DISCLAIMER}"""

    thinking_md = reasoning.get("thinking_trace", "No reasoning trace available.")

    rights_md = "### 🛡️ Your Rights\n\n"
    for r in reasoning.get("your_rights", []):
        rights_md += f"- **{r.get('right', '')}**\n  - *Source: {r.get('source', 'N/A')}*\n\n"

    options_md = "### ⚖️ Your Options\n\n"
    for o in reasoning.get("your_options", []):
        options_md += (
            f"- **{o.get('option', '')}**\n"
            f"  - Pros: {o.get('pros', 'N/A')} | Cons: {o.get('cons', 'N/A')}\n\n"
        )

    steps_md = "### 📋 Action Steps\n\n"
    for s in reasoning.get("action_steps", []):
        steps_md += (
            f"**Step {s.get('step', '?')}:** {s.get('action', '')}\n"
            f"- **Where:** {s.get('where', 'N/A')}\n"
            f"- **Deadline:** {s.get('deadline', 'N/A')}\n"
            f"- **Documents:** {s.get('documents_needed', 'N/A')}\n\n"
        )

    citations_md = "### 📚 Grounded Legal Sources (RAG)\n\n"
    for c in clauses:
        citations_md += (
            f"- **{c['act_name']}, {c['section']}** — {c['plain_summary'][:120]}...\n"
            f"  - Authority: {c.get('authority_to_approach', 'N/A')}\n\n"
        )

    action_md = rights_md + options_md + steps_md + citations_md + f"\n{DISCLAIMER}"

    return {
        "summary_md": summary_md,
        "urgency_md": urgency_md,
        "thinking_md": thinking_md,
        "action_md": action_md,
        "draft_text": draft_text.strip(),
        "extracted": extracted,
        "reasoning": reasoning,
        "clauses": clauses,
    }
