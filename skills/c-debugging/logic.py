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
        lines = [
            "## Debugging hints (not a fix or line number)",
            "",
            "**Status**: Need a bit more context to suggest angles.",
            "",
        ]
        lines.append("### What to paste next")
        for e in errors:
            lines.append(f"- {e}")
        if questions_to_ask:
            for q in questions_to_ask:
                lines.append(f"- {q}")
        return "\n".join(lines).rstrip() + "\n"

    lines: List[str] = [
        "## Debugging hints (hints only — confirm with your own checks)",
        "",
        "**First angle to explore** (ranked heuristic — not a diagnosis):",
    ]
    if likely_root_causes:
        top = likely_root_causes[0]
        conf = top.get("confidence")
        conf_pct = f"{int(round(float(conf) * 100))}%" if isinstance(conf, (int, float)) else "?"
        lines.append(f"- {top.get('title')} (relative weight {conf_pct} — still verify)")

        ev = top.get("evidence") or []
        if ev:
            lines.append("")
            lines.append("### What in your logs/code suggests looking here")
            for item in ev[:3]:
                lines.append(f"- {item}")

        checks = top.get("what_to_check") or []
        if checks:
            lines.append("")
            lines.append("### Questions / checks for you to run")
            for item in checks[:4]:
                lines.append(f"- {item}")
    else:
        lines.append("- (No strong pattern match in the snippet — use the steps below to narrow systematically.)")

    if next_steps:
        lines.append("")
        lines.append("### Process ideas (you choose what fits your setup)")
        for i, step in enumerate(next_steps[:6], start=1):
            lines.append(f"{i}. {step}")

    if questions_to_ask:
        lines.append("")
        lines.append("### Clarifying questions")
        for q in questions_to_ask[:5]:
            lines.append(f"- {q}")

    if warnings:
        lines.append("")
        lines.append("### Notes")
        for w in warnings[:5]:
            lines.append(f"- {w}")

    return "\n".join(lines).rstrip() + "\n"


def _pedagogy_meta() -> Dict[str, Any]:
    return {
        "intent": "c_debug_hints",
        "hints_only": True,
        "note": "Investigation angles and process steps — not line-level fixes or definitive root cause.",
    }


def run(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    CS-213 style C debugging triage — hint-oriented.

    Ranks *investigation angles* and process steps. Callers/agents must not treat output as
    “the bug” or “the fix”; students still locate the issue and decide changes themselves.
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
            "pedagogy": _pedagogy_meta(),
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
                "Prototype / header consistency",
                0.75,
                ["Compiler mentions implicit declaration / prototype mismatch."],
                [
                    "Which header declares the function you’re calling, and does your call’s arity/types match that declaration?",
                    "If you comment out the call temporarily, does the warning move — what does that tell you about where the mismatch lives?",
                ],
            )
        )
    if _contains_any(compiler_output, ["format specifies type", "format '%", "warning: format", "printf"]):
        likely.append(
            _make_hypothesis(
                "Format string vs actual argument types",
                0.7,
                ["Compiler warns about format specifier/type mismatch."],
                [
                    "Walk each `%...` left-to-right: what type is the matching argument? Where might they disagree?",
                    "For pointer arguments, what would you need to print for the type to be honest with `%p`?",
                ],
            )
        )
    if _contains_any(compiler_output, ["control reaches end of non-void function", "non-void function does not return"]):
        likely.append(
            _make_hypothesis(
                "All paths return a value (non-void function)",
                0.65,
                ["Compiler warns non-void function may not return."],
                [
                    "Trace each return path: is there any branch that falls off the end without returning?",
                    "What would a sensible return be on the “missing” path — or is the control flow itself incomplete?",
                ],
            )
        )

    # --- Runtime crash patterns ---
    if _contains_any(blob, ["segmentation fault", "segfault", "sigsegv", "bus error", "sigbus"]):
        evidence = ["Crash indicates invalid memory access (SIGSEGV/SIGBUS)."]

        # Null deref
        if re.search(r"\bNULL\b", c_code) and re.search(r"\*\s*\w+", c_code):
            likely.append(
                _make_hypothesis(
                    "Pointer validity before `*` (null is one case)",
                    0.8,
                    evidence + ["Snippet shows NULL and a dereference-shaped use of a pointer."],
                    [
                        "Immediately before the crashing dereference: where could that pointer’s value have been set, and can it still be NULL?",
                        "If NULL is allowed by the design, what should the function do instead of dereferencing?",
                    ],
                )
            )
        else:
            likely.append(
                _make_hypothesis(
                    "Bad value used at a dereference or indexing site",
                    0.65,
                    evidence,
                    [
                        "From a backtrace, which *expression* is the crash on — what values can that pointer or index take one step earlier?",
                        "How would you tell apart NULL vs uninitialized vs out-of-bounds from evidence (print, gdb `print`, sanitizer) without assuming?",
                        "If there’s an array: what relationship must hold between index and size for this access to be valid?",
                    ],
                )
            )

    if _contains_any(blob, ["use-after-free", "invalid read", "invalid write", "heap-use-after-free", "double free", "corrupted"]):
        likely.append(
            _make_hypothesis(
                "Heap lifetime / pairing (free vs use)",
                0.8,
                ["Tool/runtime output suggests invalid heap access/free."],
                [
                    "Can you draw the allocation points and every path that reaches `free` — is there a path that uses storage after it might have been freed?",
                    "What invariant do you want about each pointer after `free` — how would you enforce it in the code you have?",
                ],
            )
        )

    if _contains_any(blob, ["stack smashing", "stack-smashing detected", "*** stack smashing detected ***", "buffer overflow"]):
        likely.append(
            _make_hypothesis(
                "Writes past the end of a stack buffer",
                0.85,
                ["Runtime indicates stack smashing/buffer overflow."],
                    [
                        "Which locals are fixed-size buffers, and which operations write into them — how is the bound known at compile time vs run time?",
                        "What would you compare (intended length vs buffer size) before trusting a copy or format into that buffer?",
                    ],
            )
        )

    if _contains_any(blob, ["uninitialized", "conditional jump", "may be used uninitialized"]):
        likely.append(
            _make_hypothesis(
                "Read before write on a local or branch",
                0.7,
                ["Output mentions uninitialized use."],
                [
                    "For the variable the compiler names: list every path that reaches a read — is there a path where no write happened first?",
                    "In a loop, is the first iteration special — could the read happen before the intended initialization?",
                ],
            )
        )

    # --- C code structure heuristics ---
    if re.search(r"\bmalloc\s*\(", c_code) and not re.search(r"\bfree\s*\(", c_code):
        likely.append(
            _make_hypothesis(
                "malloc/free pairing on all paths (snippet heuristic)",
                0.45,
                ["malloc appears in code but free does not (in provided snippet)."],
                [
                    "If this snippet is complete: walk each success and error return — does every allocated pointer still have a matching release story?",
                    "What early returns or error branches might skip the cleanup you expect?",
                ],
            )
        )

    if re.search(r"\bstrcpy\s*\(|\bstrcat\s*\(|\bsprintf\s*\(", c_code):
        likely.append(
            _make_hypothesis(
                "Unbounded string write into a fixed buffer",
                0.55,
                ["Use of strcpy/strcat/sprintf detected."],
                [
                    "What is the smallest destination size this call could need, and what is the actual buffer size?",
                    "How would you express the copy so the maximum written bytes is never larger than the buffer minus NUL?",
                ],
            )
        )

    if re.search(r"\bscanf\s*\(", c_code) and re.search(r"%s", c_code):
        likely.append(
            _make_hypothesis(
                "scanf `%s` and buffer size agreement",
                0.55,
                ["scanf with %s detected."],
                [
                    "What is the maximum number of non-whitespace characters that can land in your buffer — does `%s` cap that?",
                    "What alternative input strategy would let you bound bytes read explicitly?",
                ],
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
                "If it crashes: use `bt` to see the call stack, then in the frame where you stop, inspect the *values* involved in the faulting expression (`print`, `info locals`) — interpret what they imply.",
            ]
        )
    # Always useful regardless of tools.
    next_steps.extend(
        [
            "Turn warnings on: compile with `-Wall -Wextra -g` and treat each warning as a hypothesis to verify, not noise to silence.",
            "For a segfault: identify the faulting expression from the tool output, then ask what must be true about each sub-value for that expression to be legal.",
        ]
    )

    likely_out = likely[:10]
    out = {
        "ok": True,
        "pedagogy": _pedagogy_meta(),
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