"""Compatibility shims for Kaggle + Gradio + newest huggingface_hub."""

from __future__ import annotations


def patch_huggingface_hub_for_gradio() -> None:
    """Gradio 4.44 imports HfFolder; newer huggingface_hub removed it."""
    try:
        import huggingface_hub as hub
    except ImportError:
        return

    if hasattr(hub, "HfFolder"):
        return

    class HfFolder:
        @classmethod
        def get_token(cls):
            try:
                return hub.get_token()
            except Exception:
                return None

        @classmethod
        def save_token(cls, token: str) -> None:
            # Best-effort for environments that still call save_token
            try:
                hub.login(token=token, add_to_git_credential=False)
            except Exception:
                pass

        @classmethod
        def delete_token(cls) -> None:
            try:
                hub.logout()
            except Exception:
                pass

    hub.HfFolder = HfFolder
