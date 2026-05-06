from __future__ import annotations

import importlib.util
import json
import os
import sys
from typing import Any, Dict, List, Optional


SYSTEM_PROMPT = """You are a friendly CS-213 interactive tutor.

You are helping a student understand how the stack changes as x86-64 code runs.

Guidelines:
- Be conversational and supportive, but stay technically correct.
- Prefer short explanations + concrete observations from the trace.
- When you reference the stack, use rsp/rbp, offsets, and labels (saved_rbp, return_address, locals).
- If the student is missing initial registers/memory, ask for it and suggest a reasonable default.
- When uncertain, say what you assume (e.g., "Assuming Intel syntax" or "Assuming rsp starts at 0x1000").
"""


def _load_stack_visualizer_logic():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "logic.py")
    spec = importlib.util.spec_from_file_location("_stack_visualizer_logic", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load stack_visualizer logic module spec.")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def _require_gemini():
    try:
        # Preferred import for the modern SDK.
        from google import genai  # type: ignore

        return genai
    except Exception:
        try:
            # Some environments expose it as a submodule.
            import google.genai as genai  # type: ignore

            return genai
        except Exception:
            print("error: Gemini SDK not available in this Python environment.")
            print("Install it into this repo’s .venv with:")
            print('  "./.venv/bin/python" -m pip install -r "requirements.txt"')
            raise


def _read_multiline(prompt: str) -> str:
    print(prompt)
    print("(finish with a single line containing only `.`)")
    lines: List[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == ".":
            break
        lines.append(line)
    return "\n".join(lines).rstrip() + "\n"


def _parse_json_dict(s: str) -> Dict[str, Any]:
    s = (s or "").strip()
    if not s:
        return {}
    try:
        v = json.loads(s)
        return v if isinstance(v, dict) else {}
    except Exception:
        return {}


def _compact_timeline(out: Dict[str, Any], max_steps: int = 12, max_slots: int = 8) -> str:
    timeline = out.get("timeline") or []
    if not isinstance(timeline, list):
        return "(no timeline)"

    chunks: List[str] = []
    for t in timeline[:max_steps]:
        if not isinstance(t, dict):
            continue
        step = t.get("step")
        asm = (t.get("asm") or "").strip()
        ch = t.get("change") or {}
        rsp_b = ch.get("rsp_before")
        rsp_a = ch.get("rsp_after")
        mw = ch.get("mem_write")

        def hx(x: Any) -> str:
            return hex(x) if isinstance(x, int) else str(x)

        chunks.append(f"step {step}: {asm}")
        chunks.append(f"  rsp: {hx(rsp_b)} -> {hx(rsp_a)}")
        if isinstance(mw, dict) and mw.get("kind") == "mem":
            chunks.append(f"  mem_write: [{hx(mw.get('addr'))}] = {hx(mw.get('value'))}")

        slots = t.get("slots") or []
        if isinstance(slots, list) and slots:
            chunks.append("  stack window:")
            for s in slots[:max_slots]:
                if not isinstance(s, dict):
                    continue
                addr = s.get("addr")
                off = s.get("offset_from_rbp")
                val = s.get("value")
                label = s.get("label")
                chunks.append(f"    {hx(addr)}  off_rbp={off}  val={hx(val) if val is not None else 'None'}  label={label}")
        chunks.append("")

    return "\n".join(chunks).rstrip() + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    _ = argv  # reserved (we keep it interactive for now)

    genai = _require_gemini()
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("error: missing GEMINI_API_KEY (or GOOGLE_API_KEY) in environment.")
        print("Set it like:")
        print('  export GEMINI_API_KEY="...your key..."')
        return 2

    client = genai.Client(api_key=api_key)
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    sv = _load_stack_visualizer_logic()

    print("Interactive Stack Tutor (Gemini)")
    print("- Paste assembly and we’ll walk the stack step-by-step.")
    print("- Commands: /asm, /state, /run, /quit")
    print("")

    asm = ""
    state: Dict[str, Any] = {"regs": {"rsp": 0x1000, "rbp": 0x0}, "mem": {}}
    history: List[Dict[str, str]] = [{"role": "user", "parts": SYSTEM_PROMPT}]

    while True:
        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("")
            break

        if not cmd:
            continue
        if cmd in ("/quit", "/exit"):
            break

        if cmd == "/asm":
            asm = _read_multiline("Paste assembly (Intel or AT&T).")
            continue

        if cmd == "/state":
            print("Current initial_state JSON:")
            print(json.dumps(state, indent=2, sort_keys=True))
            s = input("Paste new JSON (or blank to keep): ").strip()
            if s:
                parsed = _parse_json_dict(s)
                if parsed:
                    state = parsed
                else:
                    print("Couldn’t parse JSON; keeping previous state.")
            continue

        if cmd == "/run":
            if not asm.strip():
                print("No asm set yet. Use /asm first.")
                continue

            trace = sv.run(
                {
                    "asm": asm,
                    "syntax": "auto",
                    "initial_state": state,
                    "max_steps": 80,
                    "max_slots": 14,
                }
            )
            compact = _compact_timeline(trace, max_steps=12, max_slots=8)

            user_msg = (
                "Here is the stack trace timeline for the student’s code.\n\n"
                + compact
                + "\nNow tutor the student: explain what happened to the stack, highlight saved rbp/return address/locals, "
                + "and ask one good follow-up question."
            )
            history.append({"role": "user", "parts": user_msg})

            resp = client.models.generate_content(model=model, contents=history)
            text = getattr(resp, "text", None) or ""
            print("\n" + text.strip() + "\n")
            history.append({"role": "model", "parts": text})
            continue

        # Free-form question: answer using last-known asm/state if present.
        if asm.strip():
            trace = sv.run({"asm": asm, "syntax": "auto", "initial_state": state, "max_steps": 40, "max_slots": 12})
            compact = _compact_timeline(trace, max_steps=8, max_slots=6)
            user_msg = f"Student question: {cmd}\n\nContext (timeline):\n{compact}"
        else:
            user_msg = f"Student question: {cmd}"

        history.append({"role": "user", "parts": user_msg})
        resp = client.models.generate_content(model=model, contents=history)
        text = getattr(resp, "text", None) or ""
        print("\n" + text.strip() + "\n")
        history.append({"role": "model", "parts": text})

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

