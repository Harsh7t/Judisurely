"""Gradio web UI for Nyay Mitra."""

from utils.hf_compat import patch_huggingface_hub_for_gradio

patch_huggingface_hub_for_gradio()

import gradio as gr

from utils.pdf_generator import generate_pdf
from utils.pipeline import analyze_notice
from utils.schemas import DISCLAIMER, TEMPLATE_NAMES


def _get_file_path(file):
    """Normalize Gradio file upload to a local path."""
    if file is None:
        return None
    if isinstance(file, str):
        return file
    if hasattr(file, "name"):
        return file.name
    return str(file)


def run_analysis(image, text, file, language, template_key):
    """Gradio handler for analyze button."""
    file_path = _get_file_path(file)
    result = analyze_notice(
        image=image,
        text=text or "",
        file_path=file_path,
        language=language,
        template_key=template_key,
    )

    if "error" in result:
        err = result["error"]
        return err, err, err, err, "", None

    return (
        result["summary_md"],
        result["urgency_md"],
        result["thinking_md"],
        result["action_md"],
        result["draft_text"],
        None,
    )


def run_pdf_export(draft_text):
    """Generate PDF from draft text box."""
    if not draft_text or not draft_text.strip():
        return None
    return generate_pdf(draft_text)


def build_demo():
    """Build and return Gradio Blocks app."""
    with gr.Blocks(
        title="Nyay Mitra - AI Legal Action Engine",
        theme=gr.themes.Soft(primary_hue="orange"),
    ) as demo:
        gr.Markdown(
            """# ⚖️ Nyay Mitra — AI Legal Action Engine
*Upload a legal notice → Understand your rights → Get your action plan → Download your draft*

**Powered by Gemma 4** | Track 1: AI for Legal Assistance | Build with Gemma – AIMS DTU
"""
        )
        gr.Markdown(DISCLAIMER)

        with gr.Row():
            with gr.Column(scale=1):
                input_image = gr.Image(label="📄 Upload notice image", type="pil")
                input_file = gr.File(
                    label="Or upload PDF / TXT",
                    file_types=[".pdf", ".txt", ".png", ".jpg", ".jpeg"],
                )
                input_text = gr.Textbox(
                    label="Or paste notice text",
                    lines=8,
                    placeholder="Paste the full text of your legal notice here...",
                )
                lang_select = gr.Radio(
                    ["English", "Hindi"],
                    label="🌐 Output language",
                    value="English",
                )
                template_select = gr.Dropdown(
                    choices=list(TEMPLATE_NAMES.keys()),
                    value="legal_reply",
                    label="📝 Draft template",
                    info="Display names: "
                    + ", ".join(TEMPLATE_NAMES.values()),
                )
                analyze_btn = gr.Button("🔍 Analyze My Notice", variant="primary", size="lg")

            with gr.Column(scale=2):
                with gr.Tabs():
                    with gr.Tab("📊 Summary & Risk"):
                        summary_out = gr.Markdown()
                        urgency_out = gr.Markdown()
                        with gr.Accordion("🧠 Thinking Mode — AI Reasoning Trace", open=False):
                            thinking_out = gr.Markdown()

                    with gr.Tab("🛡️ Action Plan"):
                        action_out = gr.Markdown()

                    with gr.Tab("📝 Legal Draft"):
                        draft_out = gr.Textbox(
                            label="Auto-generated draft (editable)",
                            lines=18,
                        )
                        with gr.Row():
                            pdf_btn = gr.Button("⬇️ Download as PDF", variant="secondary")
                            pdf_out = gr.File(label="Your PDF")

        analyze_btn.click(
            fn=run_analysis,
            inputs=[input_image, input_text, input_file, lang_select, template_select],
            outputs=[summary_out, urgency_out, thinking_out, action_out, draft_out, pdf_out],
        )

        pdf_btn.click(fn=run_pdf_export, inputs=[draft_out], outputs=[pdf_out])

        gr.Markdown(
            "---\n"
            "**How it works:** Gemma 4 extracts your notice → RAG retrieves verified legal clauses → "
            "Gemma reasons about your rights and next steps → Gemma generates your draft reply.\n\n"
            f"{DISCLAIMER}"
        )

    return demo


def launch(share: bool = False):
    """Launch Gradio app."""
    demo = build_demo()
    demo.launch(share=share, debug=False, show_api=False)


if __name__ == "__main__":
    launch(share=True)
