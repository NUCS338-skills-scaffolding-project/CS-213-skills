from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Union


def _as_text(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    return str(x)


def _symptoms_text(symptoms: Union[str, List[str], None]) -> str:
    if symptoms is None:
        return ""
    if isinstance(symptoms, list):
        return "\n".join(_as_text(s) for s in symptoms)
    return _as_text(symptoms)


def _contains_any(text: str, needles: List[str]) -> bool:
    t = text.lower()
    return any(n.lower() in t for n in needles)


def _make_hypothesis(title: str, confidence: float, evidence: List[str], what_to_check: List[str]) -> Dict[str, Any]:
    confidence = max(0.0, min(1.0, float(confidence)))
    return {
        "title": title,
        "confidence": confidence,
        "evidence": evidence,
        "what_to_check": what_to_check,
    }


def _format_message(
    *,
    likely_root_causes: List[Dict[str, Any]],
    questions_to_ask: List[str],
    next_steps: List[str],
    warnings: List[str],
    errors: List[str],
) -> str:
    if errors:
        lines = ["## Debugging result", "", "**Status**: I’m missing a bit of info to narrow this down.", ""]
        lines.append("### What I need from you")
        for e in errors:
            lines.append(f"- {e}")
        if questions_to_ask:
            for q in questions_to_ask:
                lines.append(f"- {q}")
        return "\n".join(lines).rstrip() + "\n"

    lines: List[str] = ["## Debugging result", "", "**Best guess (based on what you shared)**:"]
    if likely_root_causes:
        top = likely_root_causes[0]
        conf = top.get("confidence")
        conf_pct = f"{int(round(float(conf) * 100))}%" if isinstance(conf, (int, float)) else "?"
        lines.append(f"- {top.get('title')} ({conf_pct} confidence)")

        ev = top.get("evidence") or []
        if ev:
            lines.append("")
            lines.append("### Why I think that")
            for item in ev[:3]:
                lines.append(f"- {item}")

        checks = top.get("what_to_check") or []
        if checks:
            lines.append("")
            lines.append("### Quick things to check next")
            for item in checks[:4]:
                lines.append(f"- {item}")
    else:
        lines.append("- (Nothing clearly matches yet — but we can still debug this systematically.)")

    if next_steps:
        lines.append("")
        lines.append("### Good next steps to try")
        for i, step in enumerate(next_steps[:6], start=1):
            lines.append(f"{i}. {step}")

    if questions_to_ask:
        lines.append("")
        lines.append("### A couple quick questions (to narrow it down)")
        for q in questions_to_ask[:5]:
            lines.append(f"- {q}")

    if warnings:
        lines.append("")
        lines.append("### Notes")
        for w in warnings[:5]:
            lines.append(f"- {w}")

    return "\n".join(lines).rstrip() + "\n"


def run(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    CS-213 style C debugging triage.

    This function is intentionally heuristic: it ranks common root causes and emits concrete next steps.
    """
    c_code = _as_text((input or {}).get("c_code"))
    compiler_output = _as_text((input or {}).get("compiler_output"))
    runtime_output = _as_text((input or {}).get("runtime_output"))
    symptoms = _symptoms_text((input or {}).get("symptoms"))
    constraints = (input or {}).get("constraints", {}) or {}
    tools_allowed = constraints.get("tools_allowed")
    if isinstance(tools_allowed, list):
        tools_allowed = [str(t).lower() for t in tools_allowed]
    else:
        tools_allowed = []

    blob = "\n".join([c_code, compiler_output, runtime_output, symptoms]).strip()
    warnings: List[str] = []
    errors: List[str] = []

    if not blob:
        return {
            "ok": False,
            "likely_root_causes": [],
            "questions_to_ask": ["Can you paste the C code and the exact compiler/runtime output (copy/paste is perfect)?"],
            "next_steps": [],
            "warnings": [],
            "errors": ["No input context provided (expected at least one of c_code/compiler_output/runtime_output/symptoms)."],
            "message": _format_message(
                likely_root_causes=[],
                questions_to_ask=["Can you paste the C code and the exact compiler/runtime output (copy/paste is perfect)?"],
                next_steps=[],
                warnings=[],
                errors=["No input context provided (expected at least one of c_code/compiler_output/runtime_output/symptoms)."],
            ),
        }

    likely: List[Dict[str, Any]] = []

    # --- Compiler-side patterns ---
    if _contains_any(compiler_output, ["implicit declaration", "incompatible implicit declaration", "implicit-int"]):
        likely.append(
            _make_hypothesis(
                "Missing header / wrong function prototype",
                0.75,
                ["Compiler mentions implicit declaration / prototype mismatch."],
                ["Include the correct header (e.g., <string.h>, <stdlib.h>)", "Ensure function signatures match (args + return type)."],
            )
        )
    if _contains_any(compiler_output, ["format specifies type", "format '%", "warning: format", "printf"]):
        likely.append(
            _make_hypothesis(
                "printf/scanf format string mismatch",
                0.7,
                ["Compiler warns about format specifier/type mismatch."],
                ["Match specifiers: %d(int), %ld(long), %p(void*), %zu(size_t)", "For pointers use %p with (void*)ptr cast."],
            )
        )
    if _contains_any(compiler_output, ["control reaches end of non-void function", "non-void function does not return"]):
        likely.append(
            _make_hypothesis(
                "Missing return in non-void function",
                0.65,
                ["Compiler warns non-void function may not return."],
                ["Ensure all paths return a value", "Add a default return at end only if logically correct."],
            )
        )

    # --- Runtime crash patterns ---
    if _contains_any(blob, ["segmentation fault", "segfault", "sigsegv", "bus error", "sigbus"]):
        evidence = ["Crash indicates invalid memory access (SIGSEGV/SIGBUS)."]

        # Null deref
        if re.search(r"\bNULL\b", c_code) and re.search(r"\*\s*\w+", c_code):
            likely.append(
                _make_hypothesis(
                    "NULL pointer dereference",
                    0.8,
                    evidence + ["Code contains NULL and a dereference pattern."],
                    [
                        "Before any dereference, confirm the pointer has been assigned a valid address (from `malloc`, or the address of an in-scope object).",
                        "If NULL is a possible state, decide what behavior should happen in that case (return an error, skip work, etc.).",
                    ],
                )
            )
        else:
            likely.append(
                _make_hypothesis(
                    "Invalid pointer dereference (null/uninitialized/out-of-bounds)",
                    0.65,
                    evidence,
                    [
                        "Use a backtrace to identify the call path leading to the crash (don’t jump to conclusions from one frame).",
                        "Right before the crash, inspect the *values* of pointers/indices involved in the dereference (are they NULL? uninitialized? out of range?).",
                        "If arrays are involved, sanity-check index bounds and the allocated length/capacity.",
                    ],
                )
            )

    if _contains_any(blob, ["use-after-free", "invalid read", "invalid write", "heap-use-after-free", "double free", "corrupted"]):
        likely.append(
            _make_hypothesis(
                "Heap misuse (use-after-free / double-free / invalid free)",
                0.8,
                ["Tool/runtime output suggests invalid heap access/free."],
                ["Ensure each malloc has exactly one free", "Set pointers to NULL after free and avoid dereferencing freed pointers."],
            )
        )

    if _contains_any(blob, ["stack smashing", "stack-smashing detected", "*** stack smashing detected ***", "buffer overflow"]):
        likely.append(
            _make_hypothesis(
                "Stack buffer overflow",
                0.85,
                ["Runtime indicates stack smashing/buffer overflow."],
                ["Check fixed-size arrays and string ops (strcpy/gets/sprintf)", "Use bounded functions and validate lengths."],
            )
        )

    if _contains_any(blob, ["uninitialized", "conditional jump", "may be used uninitialized"]):
        likely.append(
            _make_hypothesis(
                "Uninitialized variable used",
                0.7,
                ["Output mentions uninitialized use."],
                ["Initialize locals before reading", "In loops, ensure all paths assign before use."],
            )
        )

    # --- C code structure heuristics ---
    if re.search(r"\bmalloc\s*\(", c_code) and not re.search(r"\bfree\s*\(", c_code):
        likely.append(
            _make_hypothesis(
                "Memory leak (malloc without free)",
                0.45,
                ["malloc appears in code but free does not (in provided snippet)."],
                ["Ensure every allocated block is freed on all control-flow paths", "Be careful with early returns and error handling."],
            )
        )

    if re.search(r"\bstrcpy\s*\(|\bstrcat\s*\(|\bsprintf\s*\(", c_code):
        likely.append(
            _make_hypothesis(
                "Potential unsafe string operation (overflow risk)",
                0.55,
                ["Use of strcpy/strcat/sprintf detected."],
                ["Prefer strncpy/strncat/snprintf with correct bounds", "Ensure destination buffer is large enough (including NUL byte)."],
            )
        )

    if re.search(r"\bscanf\s*\(", c_code) and re.search(r"%s", c_code):
        likely.append(
            _make_hypothesis(
                "scanf %s without width limit (overflow risk)",
                0.55,
                ["scanf with %s detected."],
                ["Add width specifier: %Ns", "Prefer fgets then parse."],
            )
        )

    # Rank hypotheses by confidence, then stable by insertion order.
    likely = sorted(likely, key=lambda h: h["confidence"], reverse=True)

    # Questions to ask: only if missing context.
    questions: List[str] = []
    if not compiler_output.strip():
        questions.append("What exact gcc/clang command and full compiler output (warnings included) do you get?")
    if not runtime_output.strip() and not symptoms.strip():
        questions.append("What happens when you run it (exact output/crash message)?")
    if "gdb" in tools_allowed:
        questions.append("If you run in gdb, what is the backtrace at the crash?")

    # Next steps: adapt to allowed tools.
    next_steps: List[str] = []
    if "asan" in tools_allowed:
        next_steps.append("Recompile with AddressSanitizer: add `-fsanitize=address -fno-omit-frame-pointer -g`, then rerun.")
    if "ubsan" in tools_allowed:
        next_steps.append("Recompile with UBSan: add `-fsanitize=undefined -g`, then rerun.")
    if "valgrind" in tools_allowed:
        next_steps.append("Run Valgrind: `valgrind --leak-check=full --track-origins=yes ./a.out` (or your binary).")
    if "gdb" in tools_allowed:
        next_steps.extend(
            [
                "Start gdb: `gdb --args ./your_program ...` then type `run`.",
                "If it crashes: run `bt` to see *where you are* in the call stack, then inspect locals/arguments in the current frame (e.g., `info locals`, `print ptr`, `print i`).",
            ]
        )
    # Always useful regardless of tools.
    next_steps.extend(
        [
            "Turn warnings on: compile with `-Wall -Wextra -g` and treat warnings as *leads* (they often correlate with the underlying issue).",
            "If it’s a segfault: focus on the dereference/indexing operation that *uses* a bad value; verify the pointer/index is valid immediately before it’s used.",
        ]
    )

    likely_out = likely[:10]
    out = {
        "ok": True,
        "likely_root_causes": likely_out,
        "questions_to_ask": questions,
        "next_steps": next_steps,
        "warnings": warnings,
        "errors": errors,
    }
    out["message"] = _format_message(
        likely_root_causes=likely_out,
        questions_to_ask=questions,
        next_steps=next_steps,
        warnings=warnings,
        errors=errors,
    )
    return out