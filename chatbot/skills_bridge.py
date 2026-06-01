"""Load repo skills and build a bounded text block for the LLM (tutoring context, not answers)."""
from __future__ import annotations

import importlib.util
import os
import re
from typing import Any, Callable, Dict, List

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Keep model context readable; skills are hints only.
_MAX_CHARS_TOTAL = 7500
_MAX_CHARS_C_DEBUG = 2200
_MAX_TRACE_STEPS_SHOWN = 6
_MAX_STACK_MILESTONES = 4
_MAX_CHARS_ASM_TRANSLATION = 1800
_MAX_CHARS_TRACE_BLOCK = 2600


def _wants_walkthrough(text: str) -> bool:
    t = text.lower()
    return any(
        k in t
        for k in (
            "step by step",
            "step-by-step",
            "walk me through",
            "walk through",
            "trace it",
            "hand trace",
            "show the trace",
        )
    )


def _md_bullets(items: List[str], *, limit: int = 6) -> str:
    out: List[str] = []
    for it in items[:limit]:
        it = str(it).strip()
        if it:
            out.append(f"- {it}")
    return "\n".join(out)


def _format_asm_translation(at: Dict[str, Any]) -> str:
    """
    Convert skill output into a compact TA-style checklist (markdown).
    """
    if not isinstance(at, dict) or not at.get("ok"):
        return "- (assembly_translation unavailable)"
    checklist = at.get("checklist") or []
    if not isinstance(checklist, list):
        return "- (no checklist)"

    lines: List[str] = []
    for step in checklist[:5]:
        if not isinstance(step, dict):
            continue
        title = step.get("step") or "Step"
        hints = step.get("hints") or []
        if not isinstance(hints, list):
            hints = [str(hints)]
        lines.append(f"**{title}**")
        b = _md_bullets([str(h) for h in hints], limit=2)
        lines.append(b if b else "- (no hints)")
        lines.append("")
    return "\n".join(lines).strip()


def _format_trace_block(compact: Dict[str, Any], *, include_table: bool) -> str:
    if not isinstance(compact, dict):
        return "- (trace unavailable)"
    first = compact.get("first_steps") or []
    if not isinstance(first, list):
        first = []
    out: List[str] = []
    if first:
        out.append("**First steps (each line shows `rsp` + key register deltas)**")
        out.append(_md_bullets([str(x) for x in first], limit=_MAX_TRACE_STEPS_SHOWN))
    if include_table:
        tbl = compact.get("walkthrough_table_md")
        if isinstance(tbl, str) and tbl.strip():
            out.append("")
            out.append("**Walkthrough table**")
            out.append(tbl.strip())
    miles = compact.get("stack_milestones") or []
    if isinstance(miles, list) and miles:
        out.append("")
        out.append("**Stack milestones (snapshots)**")
        # Keep this short; it’s for orientation, not full memory dumps.
        for m in miles[:3]:
            if not isinstance(m, dict):
                continue
            out.append(f"- after step {m.get('after_instruction_index')}: rsp={m.get('rsp')} rbp={m.get('rbp')}")
        if include_table:
            first_m = miles[0] if miles else None
            if isinstance(first_m, dict):
                tbl = first_m.get("table_md")
                if isinstance(tbl, str) and tbl.strip():
                    out.append("")
                    out.append("**Stack table (snapshot)**")
                    out.append(tbl.strip())
    return "\n".join(out).strip()


def _load_run(skill_folder: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    path = os.path.join(_REPO_ROOT, "skills", skill_folder, "logic.py")
    spec = importlib.util.spec_from_file_location(f"_skill_{skill_folder}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "run")


def _clip(s: str, max_len: int) -> str:
    s = s.strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 25] + "\n…(truncated)…"


def extract_snippet(text: str) -> str:
    m = re.search(r"```(?:c|asm|text)?\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # If the user didn't fence code, try to extract only assembly/C-ish lines to avoid
    # prose being treated as instructions.
    keep: List[str] = []
    asm_line = re.compile(r"^\s*([A-Za-z_][\w.]*:)?\s*(mov|add|sub|imul|idiv|lea|cmp|test|push|pop|call|ret|jmp|j\w+)\b", re.I)
    c_line = re.compile(r"^\s*(#include\b|typedef\b|struct\b|if\s*\(|for\s*\(|while\s*\(|return\b|int\b|char\b|long\b|void\b)", re.I)
    for ln in text.splitlines():
        if asm_line.search(ln) or c_line.search(ln):
            keep.append(ln.rstrip())
    return ("\n".join(keep).strip()) or text.strip()


def looks_like_c(s: str) -> bool:
    return any(
        t in s
        for t in (
            ";",
            "{",
            "}",
            "#include",
            "int ",
            "char ",
            "void ",
            "malloc",
            "printf",
            "return ",
        )
    )


def looks_like_asm(s: str) -> bool:
    if "%" in s or "ptr" in s.lower():
        return True
    return bool(re.search(r"\b(mov|add|sub|push|pop|ret|call|lea)\b", s, re.IGNORECASE))


def _trace_compact(tr: Dict[str, Any], run_stack: Callable[..., Dict[str, Any]]) -> Dict[str, Any]:
    steps = tr.get("steps") or []
    if not isinstance(steps, list):
        return {"ok": tr.get("ok"), "errors": tr.get("errors"), "steps": []}

    lines: List[str] = []
    for i, st in enumerate(steps[:_MAX_TRACE_STEPS_SHOWN]):
        if not isinstance(st, dict):
            continue
        asm = (st.get("asm") or "").strip().split("\n")[0][:120]
        err = st.get("error")
        after = (st.get("after") or {}).get("regs") or {}
        rsp = after.get("rsp")
        rsp_s = hex(rsp) if isinstance(rsp, int) else str(rsp)
        delta_s = st.get("delta_summary")
        delta_part = f" | {delta_s}" if isinstance(delta_s, str) and delta_s else ""
        lines.append(f"{i}: {asm} | rsp={rsp_s}{delta_part}" + (f" | err={err}" if err else ""))

    milestones: List[Dict[str, Any]] = []
    if steps:
        idxs = {0, len(steps) - 1}
        if len(steps) > 2:
            idxs.add(len(steps) // 2)
        if len(steps) > 4:
            idxs.add(len(steps) // 4)
        for i in sorted(idxs):
            if i < 0 or i >= len(steps):
                continue
            st = steps[i]
            if not isinstance(st, dict):
                continue
            after = st.get("after") or {}
            regs = after.get("regs") or {}
            mem = after.get("mem") or {}
            if not isinstance(regs, dict) or "rsp" not in regs:
                continue
            try:
                sv = run_stack(
                    {
                        "regs": regs,
                        "mem": mem if isinstance(mem, dict) else {},
                        "max_slots": 6,
                    }
                )
                rb = regs.get("rbp")
                milestones.append(
                    {
                        "after_instruction_index": i,
                        "rsp": hex(regs["rsp"]) if isinstance(regs.get("rsp"), int) else regs.get("rsp"),
                        "rbp": hex(rb) if isinstance(rb, int) else rb,
                        "slots": (sv.get("slots") or [])[:5],
                        "table_md": sv.get("table_md"),
                    }
                )
            except Exception:
                continue
            if len(milestones) >= _MAX_STACK_MILESTONES:
                break

    return {
        "ok": tr.get("ok"),
        "errors": tr.get("errors"),
        "instruction_count": len(steps),
        "first_steps": lines,
        "walkthrough_table_md": tr.get("walkthrough_table_md"),
        "final_regs": (tr.get("final_state") or {}).get("regs"),
        "stack_milestones": milestones,
    }


def build_skill_notes(user_message: str) -> str:
    snippet = extract_snippet(user_message)
    blocks: List[str] = []
    walkthrough = _wants_walkthrough(user_message)

    blocks.append(
        "### TOOL OUTPUT (hints only)\n"
        "- Use as tutoring hints; do not treat as authoritative.\n"
        "- Prefer short, step-by-step guidance when asked.\n"
    )

    run_c = _load_run("c-debugger")
    run_asm = _load_run("asm-translation")
    run_trace = _load_run("execution-trace")
    run_stack = _load_run("stack-visualizer")

    if looks_like_c(snippet):
        r = run_c(
            {
                "c_code": snippet,
                "symptoms": user_message[:500],
                "constraints": {"tools_allowed": ["gdb", "asan", "valgrind"]},
            }
        )
        msg = r.get("message") or str(r)
        blocks.append("### c_debugging (triage / next checks)\n" + _clip(msg, _MAX_CHARS_C_DEBUG))

    if looks_like_asm(snippet):
        at = run_asm({"asm": snippet})
        blocks.append("### assembly_translation (TA-style checklist)\n" + _clip(_format_asm_translation(at), _MAX_CHARS_ASM_TRANSLATION))

        tr = run_trace(
            {
                "asm": snippet,
                "initial_state": {"regs": {"rsp": 0x1000, "rbp": 0}, "mem": {}},
            }
        )
        compact = _trace_compact(tr, run_stack)
        blocks.append(
            "### execution_trace (guided)\n"
            + _clip(_format_trace_block(compact, include_table=walkthrough), _MAX_CHARS_TRACE_BLOCK)
        )

    if len(blocks) == 1:
        blocks.append(
            "### skills\nNo C/Intel-assembly snippet was auto-detected in the user message "
            "(try a ```c``` or ```asm``` fence, or paste Intel-style instructions). "
            "You can still answer briefly as a CS213 tutor."
        )

    out = "\n\n".join(blocks)
    return _clip(out, _MAX_CHARS_TOTAL)
