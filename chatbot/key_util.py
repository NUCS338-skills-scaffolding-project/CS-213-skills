"""Load .env files and normalize Gemini API keys (strip BOM, quotes, accidental whitespace)."""
from __future__ import annotations

import os
import re
from pathlib import Path

_DOTENV_LOADED = False


def looks_like_real_gemini_key(k: str) -> bool:
    """Heuristic: AI Studio keys are usually ~39 chars and start with AIza."""
    if not k or len(k) < 30:
        return False
    low = k.lower()
    if low.startswith("your") or low.startswith("paste") or "here" in low or "example" in low:
        return False
    if k.startswith("AIza"):
        return True
    return len(k) >= 35 and k.replace("_", "").replace("-", "").isalnum()


def load_dotenv_files() -> None:
    global _DOTENV_LOADED
    if _DOTENV_LOADED:
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        _DOTENV_LOADED = True
        return
    here = Path(__file__).resolve().parent
    root = here.parent
    # Repo root .env (optional)
    load_dotenv(root / ".env", override=False)
    # chatbot/.env wins over root + over most pre-set shell vars when override=True
    load_dotenv(here / ".env", override=True)
    _DOTENV_LOADED = True


def _parse_key_from_dotenv_file(path: Path) -> str:
    """Read GEMINI_API_KEY / GOOGLE_API_KEY from a file (explicit; avoids shell export winning)."""
    if not path.is_file():
        return ""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        for prefix in ("GEMINI_API_KEY=", "GOOGLE_API_KEY="):
            if line.startswith(prefix):
                return normalize_api_key(line[len(prefix) : :])
    return ""


def normalize_api_key(raw: str | None) -> str:
    if not raw:
        return ""
    k = str(raw).strip().strip("\ufeff\u200b")  # BOM / zero-width space
    if len(k) >= 2 and k[0] == k[-1] and k[0] in "\"'":
        k = k[1:-1].strip().strip("\ufeff\u200b")
    k = re.sub(r"\s+", "", k)
    return k


def get_gemini_api_key() -> str:
    """
    Resolve API key. Prefer value from ``chatbot/.env`` on disk so a bad
    ``export GEMINI_API_KEY=...`` in the shell cannot silently override the file.
    """
    load_dotenv_files()
    here = Path(__file__).resolve().parent
    from_file = _parse_key_from_dotenv_file(here / ".env")
    from_env = normalize_api_key(
        os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    )

    if looks_like_real_gemini_key(from_file):
        return from_file
    if looks_like_real_gemini_key(from_env):
        return from_env
    # Fall back to whichever is non-empty
    return from_file or from_env
