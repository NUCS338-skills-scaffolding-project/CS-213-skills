"""TA-style helper for Intel/AT&T x86-64 → C *structure* (hints only, never emits C source)."""
from __future__ import annotations

import re
from typing import Any, Dict, List


def _syntax(asm: str) -> str:
    if "%" in asm or "$" in asm:
        return "att"
    return "intel"


_JCC = {
    "je",
    "jne",
    "jg",
    "jge",
    "jl",
    "jle",
    "ja",
    "jae",
    "jb",
    "jbe",
    "jo",
    "jno",
    "js",
    "jns",
    "jp",
    "jnp",
    "jc",
    "jnc",
    "jz",
    "jnz",
}


def _strip_comment(line: str) -> str:
    # Intel often uses ';' and AT&T often uses '#'
    return line.split("#", 1)[0].split(";", 1)[0].strip()


def _lower_mnemonic(token: str) -> str:
    # Keep it simple; strip common size suffixes like movq/movl.
    t = token.strip().lower()
    return re.sub(r"(b|w|l|q)$", "", t)


def _find_scales(s: str) -> List[int]:
    scales: List[int] = []
    # Intel addressing: [rdi+rdx*4+8]
    for m in re.finditer(r"\*\s*(1|2|4|8)\b", s):
        scales.append(int(m.group(1)))
    # AT&T addressing: (%rdi,%rdx,4)
    for m in re.finditer(r",\s*(1|2|4|8)\s*\)", s):
        scales.append(int(m.group(1)))
    return scales


def _mentions_mem(s: str) -> bool:
    return ("[" in s and "]" in s) or ("(" in s and ")" in s and "," in s)


def _guess_ret_type_hint(lines: List[str], syn: str) -> str:
    # Return is in rax/eax; 32-bit writes usually mean int-like.
    joined = "\n".join(lines).lower()
    if syn == "intel":
        if re.search(r"\b(eax)\b", joined) and not re.search(r"\b(rax)\b", joined):
            return "Return value likely fits in 32 bits (e.g., int), since code uses EAX."
        if re.search(r"\b(rax)\b", joined):
            return "Return value likely 64-bit (e.g., long/pointer), since code uses RAX."
        return "Return value is in RAX/EAX on x86-64; look for the last write to EAX/RAX before `ret`."
    # AT&T
    if re.search(r"%eax\b", joined) and not re.search(r"%rax\b", joined):
        return "Return value likely fits in 32 bits (e.g., int), since code uses %eax."
    if re.search(r"%rax\b", joined):
        return "Return value likely 64-bit (e.g., long/pointer), since code uses %rax."
    return "Return value is in %rax/%eax on x86-64; look for the last write before `ret`."


def _arg_map_hint() -> str:
    return "SysV x86-64 args: arg0=rdi, arg1=rsi, arg2=rdx (then rcx, r8, r9)."


def _scale_type_hints(scales: List[int]) -> List[str]:
    out: List[str] = []
    for sc in sorted(set(scales)):
        if sc == 4:
            out.append("Scale 4 suggests `int` array/field access (e.g., base + i*4).")
        elif sc == 8:
            out.append("Scale 8 suggests `long`/pointer/double-sized access (base + i*8).")
        elif sc in (1, 2):
            out.append(f"Scale {sc} suggests byte/short-ish access (base + i*{sc}).")
    return out


def _control_flow_hints(jumps: List[Dict[str, Any]]) -> List[str]:
    if not jumps:
        return ["No jumps detected → likely straight-line code (or jump targets not included)."]

    out: List[str] = []
    has_back = any(j.get("direction") == "backward" for j in jumps)
    has_fwd = any(j.get("direction") == "forward" for j in jumps)
    has_table = any(j.get("kind") == "jumptable" for j in jumps)

    if has_table:
        out.append("Indirect `jmp`/jump-table pattern → likely a `switch`.")
    if has_back:
        out.append("Backward jump (to an earlier label) → likely a loop (`while` / `for`).")
    if has_fwd:
        out.append("Forward conditional jump (skips code) → likely an `if`/guard.")

    # Add a compact per-jump list for orientation.
    for j in jumps[:6]:
        m = j.get("mnemonic")
        tgt = j.get("target")
        direction = j.get("direction") or "?"
        out.append(f"{m} → {tgt} ({direction})")
    return out


def _loop_iterator_hints(clean_lines: List[str], syn: str) -> List[str]:
    # Heuristic: find registers that are incremented and later compared.
    inc_regs: List[str] = []
    cmp_regs: List[str] = []

    if syn == "intel":
        for s in clean_lines:
            sl = s.lower()
            if re.search(r"\b(inc|dec)\s+(e?[a-z]{2,3}|r\d+)\b", sl):
                inc_regs.append(re.search(r"\b(inc|dec)\s+([a-z0-9]+)\b", sl).group(2))  # type: ignore[union-attr]
            m = re.search(r"\b(add|sub)\s+([a-z0-9]+)\s*,\s*1\b", sl)
            if m:
                inc_regs.append(m.group(2))
            m2 = re.search(r"\bcmp\s+([a-z0-9]+)\s*,", sl)
            if m2:
                cmp_regs.append(m2.group(1))
    else:
        for s in clean_lines:
            sl = s.lower()
            # addl $1, %eax  | incq %rcx
            m = re.search(r"\b(add|sub)[a-z]*\s+\$1\s*,\s*(%[a-z0-9]+)\b", sl)
            if m:
                inc_regs.append(m.group(2))
            m2 = re.search(r"\binc[a-z]*\s+(%[a-z0-9]+)\b", sl)
            if m2:
                inc_regs.append(m2.group(1))
            m3 = re.search(r"\bcmp[a-z]*\s+.*,\s*(%[a-z0-9]+)\b", sl)
            if m3:
                cmp_regs.append(m3.group(1))

    inc = sorted(set(inc_regs))
    cmpd = sorted(set(cmp_regs))
    out: List[str] = []
    if inc:
        out.append("Iterator candidates (being incremented/decremented): " + ", ".join(inc[:6]))
    if cmpd:
        out.append("Condition registers seen in `cmp`: " + ", ".join(cmpd[:6]))
    if inc and cmpd:
        common = [r for r in inc if r in cmpd]
        if common:
            out.append("Strong iterator guess (both updated + compared): " + ", ".join(common[:4]))
        else:
            out.append("If the iterator isn't compared directly, it may index memory while a different reg holds the bound.")
    if not out:
        out.append("Loop iterator not obvious; look for `add/inc` on a register near a backward jump, then the nearby `cmp` that feeds the jump.")
    return out


def _memory_hints(clean_lines: List[str]) -> List[str]:
    scales: List[int] = []
    disp_bytes: List[int] = []
    for s in clean_lines:
        if not _mentions_mem(s):
            continue
        scales.extend(_find_scales(s))
        # displacement like 8(%rdi) or [rdi+8]
        for m in re.finditer(r"\b(-?\d+)\s*\(", s):
            try:
                disp_bytes.append(int(m.group(1)))
            except ValueError:
                pass
        for m in re.finditer(r"\[\s*[a-z0-9]+\s*([\+\-]\s*\d+)\s*\]", s.lower()):
            try:
                disp_bytes.append(int(m.group(1).replace(" ", "")))
            except ValueError:
                pass

    out: List[str] = []
    out.extend(_scale_type_hints(scales))
    if disp_bytes:
        ds = sorted(set(disp_bytes))
        out.append("Displacements seen (bytes): " + ", ".join(str(x) for x in ds[:8]))
        out.append("Byte displacement often means `base->field` or `&arr[k]` offset; combine with scale to decide which.")
    if not out:
        out.append("No memory addressing patterns recognized (or snippet is register-only).")
    return out


def _kernel_hints(clean_lines: List[str]) -> List[str]:
    ops: List[str] = []
    for s in clean_lines:
        parts = s.split(None, 1)
        if not parts:
            continue
        op = _lower_mnemonic(parts[0])
        if op in {"add", "sub", "imul", "mul", "idiv", "and", "or", "xor", "shl", "shr", "sar"}:
            ops.append(op)
        if op in {"lea"}:
            ops.append(op)
    if not ops:
        return ["Kernel: mostly moves/branches/calls; focus on what values flow into EAX/RAX (return) or memory stores."]
    uniq = ", ".join(sorted(set(ops)))
    return [
        "Kernel ops spotted: " + uniq,
        "Translate each arithmetic op into a C operator on the destination variable; `lea` often means address math like `base + i*scale + disp`.",
    ]


def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    asm = (inp or {}).get("asm")
    if not isinstance(asm, str) or not asm.strip():
        return {"ok": False, "syntax": None, "errors": ["Missing input['asm'] (string)."]}

    syn = _syntax(asm)
    raw_lines = asm.splitlines()

    labels: Dict[str, int] = {}
    clean_lines: List[str] = []
    tokens: List[Dict[str, Any]] = []

    for idx, raw in enumerate(raw_lines):
        s = _strip_comment(raw)
        if not s:
            continue
        if s.endswith(":"):
            labels[s[:-1].strip()] = len(tokens)
            continue
        parts = s.split(None, 1)
        mnem = parts[0]
        rest = parts[1] if len(parts) > 1 else ""
        tokens.append({"i": len(tokens), "raw": raw, "s": s, "mnem": mnem, "rest": rest})
        clean_lines.append(s)

    jumps: List[Dict[str, Any]] = []
    for t in tokens:
        m0 = _lower_mnemonic(str(t["mnem"]))
        rest = str(t["rest"]).strip()
        if m0 == "jmp":
            # Indirect jump often shows up as jmp [..] or jmp *%rax
            if "*" in rest or "[" in rest:
                jumps.append({"kind": "jumptable", "mnemonic": "jmp", "target": rest, "direction": None})
            elif rest:
                jumps.append({"kind": "jmp", "mnemonic": "jmp", "target": rest, "direction": None})
            continue
        if m0 in _JCC:
            target = rest.split(None, 1)[0] if rest else ""
            direction = None
            if target in labels:
                direction = "backward" if labels[target] < int(t["i"]) else "forward"
            jumps.append({"kind": "jcc", "mnemonic": m0, "target": target or rest or "?", "direction": direction})

    checklist: List[Dict[str, Any]] = [
        {"step": "Define function signature", "hints": [_arg_map_hint(), _guess_ret_type_hint(clean_lines, syn)]},
        {"step": "Determine data types via scale", "hints": _memory_hints(clean_lines)},
        {"step": "Identify the skeleton (control flow)", "hints": _control_flow_hints(jumps)},
        {"step": "Locate the loop iterator", "hints": _loop_iterator_hints(clean_lines, syn)},
        {
            "step": "Decode memory addressing",
            "hints": [
                "Intel: `[rdi + rdx*4]` → `arg0[arg2]`-style (base + index*scale).",
                "Displacement like `8[rdi]` / `[rdi+8]` often means `ptr->field` or `&arr[1]` depending on element size.",
            ],
        },
        {"step": "Trace the logical kernel", "hints": _kernel_hints(clean_lines)},
        {
            "step": "Refactor for readability",
            "hints": [
                "Combine `cmp` + conditional jump into a clean `if (...)` or loop condition.",
                "If you see a backward `jcc`, rewrite as `while (...) { ...; i++; }` (or a `for` if init/update are adjacent).",
            ],
        },
    ]

    return {
        "ok": True,
        "syntax": syn,
        "pedagogy": {
            "intent": "assembly_to_c_hints",
            "hints_only": True,
            "note": "Structured hints for line-by-line or block-by-block translation; do not treat as a C solution.",
        },
        "checklist": checklist,
        "detected": {
            "labels": list(labels.keys())[:12],
            "jump_count": len(jumps),
            "memory_scale_examples": _find_scales("\n".join(clean_lines))[:8],
        },
        "errors": [],
    }
