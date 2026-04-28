"""Model IDs to try with google.generativeai (names change by API version / rollout)."""
from __future__ import annotations

import os
from typing import Any, List, Optional


# Short names accepted by GenerativeModel("...") — try newer / widely deployed first.
_STATIC_FALLBACK: tuple[str, ...] = (
    "gemini-2.0-flash",
    "gemini-2.0-flash-001",
    "gemini-1.5-flash-8b",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-1.5-pro-latest",
)


def model_try_order(genai: Any, preferred: Optional[str] = None) -> List[str]:
    """
    Return model short names to try, de-duplicated.
    `preferred` is usually os.environ.get('GEMINI_MODEL').
    Appends models from list_models() that support generateContent (helps when static IDs 404).
    """
    pref = (preferred or "").strip() or None
    out: List[str] = []
    if pref:
        out.append(pref)
    for n in _STATIC_FALLBACK:
        if n not in out:
            out.append(n)

    try:
        extras: List[str] = []
        flash_first: List[str] = []
        rest: List[str] = []
        for m in genai.list_models():
            name = getattr(m, "name", "") or ""
            if not name.startswith("models/"):
                continue
            short = name.split("/", 1)[1]
            methods = list(getattr(m, "supported_generation_methods", []) or [])
            if "generateContent" not in methods:
                continue
            if "gemini" not in short.lower():
                continue
            if "embed" in short.lower():
                continue
            if "flash" in short.lower():
                flash_first.append(short)
            else:
                rest.append(short)
        extras.extend(sorted(set(flash_first)))
        extras.extend(sorted(set(rest)))
        for x in extras:
            if x not in out:
                out.append(x)
    except Exception:
        pass

    return out


def preferred_model_from_env() -> str:
    return (os.environ.get("GEMINI_MODEL") or "").strip()
