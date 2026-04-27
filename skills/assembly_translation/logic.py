from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Dict, List, Optional, Tuple


_RE_COMMENT = re.compile(r"(#|;|//).*?$")
_RE_LABEL = re.compile(r"^\s*([A-Za-z_.$][\w.$]*):\s*$")


@dataclass(frozen=True)
class Operand:
    kind: str  # "reg" | "imm" | "mem" | "label" | "unknown"
    text: str  # original-ish text (trimmed)
    # Normalized fields (best-effort; only for mem)
    base: Optional[str] = None
    index: Optional[str] = None
    scale: Optional[int] = None
    disp: Optional[int] = None
    size: Optional[str] = None  # "byte"|"word"|"dword"|"qword"|None


def _strip_comments(line: str) -> str:
    return _RE_COMMENT.sub("", line).strip()


def _detect_syntax(asm: str) -> str:
    # Heuristic: AT&T uses %regs and $immediates; Intel often uses "PTR" and bare regs.
    if re.search(r"[%]\w+", asm) or re.search(r"\$\-?0x[0-9a-fA-F]+|\$\-?\d+", asm):
        return "att"
    if re.search(r"\bPTR\b|\[[^\]]+\]", asm):
        return "intel"
    # Fallback: if we see parentheses addressing, assume AT&T; else Intel.
    if "(" in asm and ")" in asm:
        return "att"
    return "intel"


def _parse_int(s: str) -> Optional[int]:
    s = s.strip()
    if not s:
        return None
    neg = False
    if s.startswith("-"):
        neg = True
        s = s[1:].strip()
    base = 10
    if s.lower().startswith("0x"):
        base = 16
        s = s[2:]
    if not re.fullmatch(r"[0-9a-fA-F]+", s):
        return None
    val = int(s, base)
    return -val if neg else val


def _norm_reg(r: str) -> str:
    r = r.strip()
    r = r.lstrip("%")
    return r.lower()


def _parse_att_mem(op: str) -> Optional[Operand]:
    # disp(base,index,scale) where any may be missing. Example: -0x8(%rbp) or (%rax,%rcx,4)
    m = re.fullmatch(r"(?P<disp>[-+]?0x[0-9a-fA-F]+|[-+]?\d+)?\((?P<body>[^)]*)\)", op.strip())
    if not m:
        return None
    disp = _parse_int(m.group("disp") or "0") or 0
    body = m.group("body").strip()
    parts = [p.strip() for p in body.split(",")] if body else []
    base = _norm_reg(parts[0]) if len(parts) >= 1 and parts[0] else None
    index = _norm_reg(parts[1]) if len(parts) >= 2 and parts[1] else None
    scale = _parse_int(parts[2]) if len(parts) >= 3 and parts[2] else None
    if scale is not None and scale not in (1, 2, 4, 8):
        scale = None
    return Operand(kind="mem", text=op.strip(), base=base, index=index, scale=scale, disp=disp)


def _parse_intel_mem(op: str) -> Optional[Operand]:
    # Examples:
    #   [rbp-8]
    #   qword ptr [rbp + rax*8 - 0x10]
    s = op.strip()
    size = None
    m_size = re.match(r"^(?P<size>(byte|word|dword|qword))\s+ptr\s+(?P<rest>.+)$", s, flags=re.IGNORECASE)
    if m_size:
        size = m_size.group("size").lower()
        s = m_size.group("rest").strip()
    m = re.fullmatch(r"\[(?P<body>[^\]]+)\]", s)
    if not m:
        return None
    body = m.group("body").strip()

    # Very small expression parser: tokens separated by +/-
    # Supports: base, index*scale, and constant displacement.
    tokens = re.split(r"(\+|\-)", body.replace(" ", ""))
    sign = +1
    base = None
    index = None
    scale = None
    disp = 0
    for t in tokens:
        if t == "+":
            sign = +1
            continue
        if t == "-":
            sign = -1
            continue
        if not t:
            continue

        # index*scale
        m_is = re.fullmatch(r"([A-Za-z][\w]*)\*(\d+)", t)
        if m_is:
            idx = _norm_reg(m_is.group(1))
            sc = int(m_is.group(2))
            if sc in (1, 2, 4, 8) and index is None:
                index, scale = idx, sc
            else:
                # can't represent multiple index terms
                return Operand(kind="mem", text=op.strip(), base=base, index=index, scale=scale, disp=disp, size=size)
            continue

        # register
        if re.fullmatch(r"[A-Za-z][\w]*", t):
            reg = _norm_reg(t)
            if base is None:
                base = reg
            elif index is None:
                index, scale = reg, 1
            else:
                return Operand(kind="mem", text=op.strip(), base=base, index=index, scale=scale, disp=disp, size=size)
            continue

        # number
        iv = _parse_int(t)
        if iv is not None:
            disp += sign * iv
            continue

        # unknown token
        return None

    return Operand(kind="mem", text=op.strip(), base=base, index=index, scale=scale, disp=disp, size=size)


def _parse_operand(op: str, syntax: str) -> Operand:
    s = op.strip()
    if not s:
        return Operand(kind="unknown", text=s)

    # Remove trailing commas
    if s.endswith(","):
        s = s[:-1].strip()

    if syntax == "att":
        if s.startswith("%"):
            return Operand(kind="reg", text=s, base=_norm_reg(s))
        if s.startswith("$"):
            return Operand(kind="imm", text=s, disp=_parse_int(s[1:]))
        mem = _parse_att_mem(s)
        if mem:
            return mem
        if re.fullmatch(r"[-+]?0x[0-9a-fA-F]+|[-+]?\d+", s):
            return Operand(kind="imm", text=s, disp=_parse_int(s))
        return Operand(kind="label", text=s)

    # intel
    if re.fullmatch(r"\[(.+)\]", s) or re.search(r"\bptr\b", s, flags=re.IGNORECASE):
        mem = _parse_intel_mem(s)
        if mem:
            return mem
    if re.fullmatch(r"[-+]?0x[0-9a-fA-F]+|[-+]?\d+", s):
        return Operand(kind="imm", text=s, disp=_parse_int(s))
    if re.fullmatch(r"[A-Za-z][\w]*", s):
        return Operand(kind="reg", text=s, base=_norm_reg(s))
    return Operand(kind="label", text=s)


def _split_operands(ops: str) -> List[str]:
    # Split on commas, but keep brackets/parentheses together.
    out: List[str] = []
    cur = []
    depth = 0
    for ch in ops:
        if ch in "[(":
            depth += 1
        elif ch in "])":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if cur:
        out.append("".join(cur).strip())
    return [o for o in out if o]


def _normalize_instruction(mnemonic: str, operands: List[Operand], syntax: str) -> Dict[str, Any]:
    m = mnemonic.lower()
    ops = operands
    # Normalize operand order: AT&T is src,dst; Intel is dst,src
    if syntax == "att" and len(ops) == 2:
        src, dst = ops[0], ops[1]
    elif syntax == "intel" and len(ops) == 2:
        dst, src = ops[0], ops[1]
    else:
        src = ops[0] if ops else None
        dst = ops[1] if len(ops) > 1 else None

    return {
        "mnemonic": m,
        "operands": [o.__dict__ for o in ops],
        "src": src.__dict__ if src else None,
        "dst": dst.__dict__ if dst else None,
    }


def _explain(instr: Dict[str, Any]) -> str:
    m = instr["mnemonic"]
    src = instr.get("src")
    dst = instr.get("dst")

    def ot(o: Optional[Dict[str, Any]]) -> str:
        return o["text"] if o else ""

    if m in ("mov", "movl", "movq", "movb", "movw"):
        return f"Copy {ot(src)} into {ot(dst)}."
    if m == "lea":
        return f"Compute address/value {ot(src)} and store in {ot(dst)} (no memory load)."
    if m in ("add", "addl", "addq"):
        return f"{ot(dst)} = {ot(dst)} + {ot(src)}."
    if m in ("sub", "subl", "subq"):
        return f"{ot(dst)} = {ot(dst)} - {ot(src)}."
    if m in ("imul", "imull", "imulq"):
        return f"{ot(dst)} = {ot(dst)} * {ot(src)} (signed multiply, heuristic)."
    if m in ("xor", "xorl", "xorq"):
        if src and dst and src["kind"] == "reg" and dst["kind"] == "reg" and src["base"] == dst["base"]:
            return f"Zero {ot(dst)} (xor reg, reg)."
        return f"{ot(dst)} = {ot(dst)} XOR {ot(src)}."
    if m in ("and", "andl", "andq"):
        return f"{ot(dst)} = {ot(dst)} AND {ot(src)}."
    if m in ("or", "orl", "orq"):
        return f"{ot(dst)} = {ot(dst)} OR {ot(src)}."
    if m in ("shl", "sal", "shll", "salq", "shr", "sar"):
        return f"Shift {ot(dst)} by {ot(src)}."
    if m in ("cmp", "cmpl", "cmpq", "test"):
        return f"Update flags based on {ot(dst)} vs {ot(src)} (no direct assignment)."
    if m.startswith("j"):
        return f"Conditional jump to {instr['operands'][0]['text'] if instr.get('operands') else '?'} based on flags."
    if m in ("push",):
        return f"Push {ot(src) or (instr['operands'][0]['text'] if instr.get('operands') else '?')} onto stack."
    if m in ("pop",):
        return f"Pop stack value into {ot(src) or (instr['operands'][0]['text'] if instr.get('operands') else '?')}."
    if m in ("call",):
        return f"Call function at {instr['operands'][0]['text'] if instr.get('operands') else '?'} (push return address)."
    if m in ("ret", "retq"):
        return "Return from function (pop return address into RIP)."
    return "Instruction not specifically recognized; shown verbatim."


def _pseudocode(lines: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
    warnings: List[str] = []
    out: List[str] = []
    for li in lines:
        instr = li.get("instruction")
        if not instr:
            continue
        m = instr["mnemonic"]
        src = instr.get("src")
        dst = instr.get("dst")

        def expr(o: Optional[Dict[str, Any]]) -> str:
            if not o:
                return "<?>"
            if o["kind"] == "reg":
                return o.get("base") or o["text"]
            if o["kind"] == "imm":
                return str(o.get("disp") if o.get("disp") is not None else o["text"])
            if o["kind"] == "mem":
                base = o.get("base")
                index = o.get("index")
                scale = o.get("scale")
                disp = o.get("disp") or 0
                terms = []
                if base:
                    terms.append(base)
                if index:
                    terms.append(f"{index}*{scale or 1}")
                if disp:
                    terms.append(f"{disp:+d}")
                inside = " + ".join(terms) if terms else "0"
                return f"*({inside})"
            return o["text"]

        if m in ("mov", "movl", "movq", "movb", "movw"):
            out.append(f"{expr(dst)} = {expr(src)};")
        elif m == "lea":
            # LEA is tricky; we display address expression, not deref.
            if src and src["kind"] == "mem":
                base = src.get("base")
                index = src.get("index")
                scale = src.get("scale")
                disp = src.get("disp") or 0
                terms = []
                if base:
                    terms.append(base)
                if index:
                    terms.append(f"{index}*{scale or 1}")
                if disp:
                    terms.append(f"{disp:+d}")
                addr = " + ".join(terms) if terms else "0"
                out.append(f"{expr(dst)} = ({addr});  // lea")
            else:
                out.append(f"{expr(dst)} = {expr(src)};  // lea (heuristic)")
                warnings.append("Some lea operands weren't recognized as address expressions.")
        elif m in ("add", "addl", "addq"):
            out.append(f"{expr(dst)} += {expr(src)};")
        elif m in ("sub", "subl", "subq"):
            out.append(f"{expr(dst)} -= {expr(src)};")
        elif m in ("imul", "imull", "imulq"):
            out.append(f"{expr(dst)} *= {expr(src)};")
        elif m in ("xor", "xorl", "xorq") and src and dst and src.get("kind") == "reg" and dst.get("kind") == "reg" and src.get("base") == dst.get("base"):
            out.append(f"{expr(dst)} = 0;")
        elif m in ("cmp", "cmpl", "cmpq", "test"):
            out.append(f"// compare/test: affects flags ({expr(dst)} ? {expr(src)})")
        elif m.startswith("j"):
            out.append(f"// {m} {expr(instr['operands'][0]) if instr.get('operands') else '<?>'}")
        elif m in ("ret", "retq"):
            out.append("return;")
        elif m == "call":
            target = instr["operands"][0]["text"] if instr.get("operands") else "<?>"
            out.append(f"{target}();")
        else:
            out.append(f"// {m} " + ", ".join(o["text"] for o in instr.get("operands", [])))

    return "\n".join(out).strip() + ("\n" if out else ""), warnings


def run(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translate x86-64 assembly snippets into pseudocode + explanations.

    Parameters in `input`:
      - asm (str): required assembly text
      - syntax (str): "att" | "intel" | "auto" (default "auto")
      - include_pseudocode (bool): default True
      - max_instructions (int): default 200
    """
    asm = (input or {}).get("asm")
    if not isinstance(asm, str) or not asm.strip():
        return {
            "ok": False,
            "syntax": None,
            "instructions": [],
            "line_map": [],
            "pseudocode": "",
            "assumptions": [],
            "warnings": [],
            "errors": ["Missing required string input['asm']."],
        }

    syntax_req = (input or {}).get("syntax", "auto")
    include_pseudo = bool((input or {}).get("include_pseudocode", True))
    max_instructions = int((input or {}).get("max_instructions", 200))
    if max_instructions <= 0:
        max_instructions = 200

    syntax = _detect_syntax(asm) if syntax_req == "auto" else str(syntax_req).lower()
    if syntax not in ("att", "intel"):
        syntax = _detect_syntax(asm)

    assumptions: List[str] = [
        "Heuristic translation intended for teaching (not a full decompiler).",
        "x86-64 target assumed; calling convention details may be omitted.",
    ]
    warnings: List[str] = []
    errors: List[str] = []

    line_map: List[Dict[str, Any]] = []
    instructions: List[Dict[str, Any]] = []
    inst_count = 0

    for raw in asm.splitlines():
        stripped = _strip_comments(raw)
        if not stripped:
            line_map.append({"raw": raw, "kind": "blank_or_comment"})
            continue
        if _RE_LABEL.match(stripped):
            line_map.append({"raw": raw, "kind": "label", "label": stripped[:-1]})
            continue

        # Tokenize: mnemonic then operands.
        parts = stripped.split(None, 1)
        mnemonic = parts[0]
        ops_s = parts[1] if len(parts) > 1 else ""
        ops_text = _split_operands(ops_s) if ops_s else []
        ops = [_parse_operand(o, syntax) for o in ops_text]
        instr = _normalize_instruction(mnemonic, ops, syntax)
        expl = _explain(instr)

        line_map.append(
            {
                "raw": raw,
                "kind": "instruction",
                "instruction": instr,
                "explanation": expl,
            }
        )
        instructions.append(instr)
        inst_count += 1
        if inst_count >= max_instructions:
            warnings.append(f"Stopped after {max_instructions} instructions (max_instructions cap).")
            break

    pseudo = ""
    if include_pseudo:
        pseudo, pseudo_warnings = _pseudocode(line_map)
        warnings.extend(pseudo_warnings)

    return {
        "ok": len(errors) == 0,
        "syntax": syntax,
        "instructions": instructions,
        "line_map": line_map,
        "pseudocode": pseudo,
        "assumptions": assumptions,
        "warnings": warnings,
        "errors": errors,
    }