"""Minimal CS-213 chat UI: Flask + Google Gemini + local skills."""
from __future__ import annotations

import os
import sys

from flask import Flask, jsonify, request, send_from_directory

# Allow `python chatbot/app.py` from repo root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gemini_models import model_try_order, preferred_model_from_env
from key_util import get_gemini_api_key

from skills_bridge import build_skill_notes

app = Flask(__name__, static_folder="static", static_url_path="")


def _invalid_api_key_help(exc: BaseException) -> str | None:
    s = str(exc).lower()
    if "api_key_invalid" in s or "api key not valid" in s or "invalid api key" in s:
        return (
            "Google rejected your API key (API_KEY_INVALID). This is not a model issue — every model will fail until the key is fixed.\n\n"
            "Do this in order:\n"
            "1) Open https://aistudio.google.com/apikey (Google AI Studio) while signed into the correct Google account.\n"
            "2) Click Create API key, copy the new key.\n"
            "3) In chatbot/.env use exactly one line (no spaces around =):\n"
            "   GEMINI_API_KEY=paste_the_key_here\n"
            "4) Restart the server: bash chatbot/run.sh\n\n"
            "Avoid: Cloud Console keys with HTTP referrer restrictions, wrong Google account, or keys pasted into .env.example / git."
        )
    return None


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    user = (data.get("message") or "").strip()
    debug = bool(data.get("debug"))
    history = data.get("history") or []
    if not user:
        return jsonify({"error": "message is required"}), 400

    key = get_gemini_api_key()
    if not key:
        return jsonify(
            {
                "error": "No API key found. Set GEMINI_API_KEY in chatbot/.env (see .env.example) or export it in your shell.",
            }
        ), 503

    # Skills are based on the latest user message (keeps tool output short).
    skill_block = build_skill_notes(user)

    try:
        import google.generativeai as genai
    except ImportError:
        return jsonify({"error": "Install dependencies: pip install -r chatbot/requirements.txt"}), 503

    genai.configure(api_key=key)

    def _wants_depth(s: str) -> bool:
        s = (s or "").lower()
        return any(k in s for k in ("detailed", "in detail", "explain", "walk me through", "step by step", "step-by-step", "show work"))

    depth = _wants_depth(user)

    system = (
        "You are a CS 213 (intro systems) tutor: C, pointers, memory, and x86-64 (Intel syntax).\n\n"
        "SKILL OUTPUT: The section labeled 'TOOL OUTPUT' is machine-generated context (assembly hints, "
        "possible C bug angles, tiny execution-trace summaries, stack snapshots). Treat it as auxiliary "
        "signal — it can be incomplete.\n\n"
        "PEDAGOGY (required):\n"
        "- Do NOT give the direct final answer to homework-style questions (no full worked solutions, no "
        "complete translated C program as the entire answer).\n"
        "- DO guide: short plan, targeted questions, what to check next, common pitfalls, and at most a "
        "tiny illustrative fragment if it helps reasoning.\n"
        "- For assembly→C: help the user map registers/memory/operations to C concepts; let them finish the mapping.\n"
        "- For tracing/stack: point them at which instruction or slot to focus on and what should change next.\n\n"
        "FORMAT (required):\n"
        "- Be concise by default, but if the user asks for depth, give a fuller explanation.\n"
        "- Prefer **3–6 short bullets** or 2 tiny paragraphs; avoid long essays and huge code dumps.\n"
        "- If you show code, keep it minimal (a few lines).\n"
    )

    # Include a small amount of chat history so the model can stay consistent across turns.
    hist_lines: list[str] = []
    if isinstance(history, list):
        for m in history[-14:]:
            if not isinstance(m, dict):
                continue
            role = (m.get("role") or "").strip().lower()
            text = (m.get("text") or "").strip()
            if not text:
                continue
            if role not in ("user", "assistant"):
                continue
            hist_lines.append(f"{'USER' if role == 'user' else 'ASSISTANT'}: {text}")
    hist_block = "\n".join(hist_lines).strip()

    prompt = (
        f"{system}\n\n"
        f"--- TOOL OUTPUT ---\n{skill_block}\n\n"
        + (f"--- CHAT HISTORY ---\n{hist_block}\n\n" if hist_block else "")
        + f"--- USER ---\n{user}"
    )

    last_err: str | None = None
    candidates = model_try_order(genai, preferred_model_from_env() or None)

    for name in candidates:
        try:
            model = genai.GenerativeModel(name)
            resp = model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": 900 if depth else 650,
                    "temperature": 0.55,
                },
            )
            try:
                text = (resp.text or "").strip()
            except ValueError:
                text = "(Model returned no text — try a different prompt or GEMINI_MODEL.)"
            payload = {"reply": text}
            if debug:
                payload["tool_notes"] = skill_block
                payload["model_used"] = name
            return jsonify(payload)
        except Exception as ex:
            bad_key = _invalid_api_key_help(ex)
            if bad_key:
                return jsonify({"error": bad_key + f"\n\nTechnical detail: [{name}] {ex}"}), 401
            last_err = f"[{name}] {ex}"

    hint = (
        " If you see 404 model not found: set GEMINI_MODEL in chatbot/.env (e.g. gemini-2.0-flash). "
        "Also try: pip install -U google-generativeai. "
        "If you see API_KEY_INVALID: new AI Studio key + chatbot/.env. "
        f"Last error: {last_err}"
    )
    return jsonify({"error": "Gemini request failed." + hint}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="127.0.0.1", port=port, debug=True)
