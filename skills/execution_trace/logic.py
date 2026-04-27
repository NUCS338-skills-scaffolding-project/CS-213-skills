from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple


MASK64 = (1 << 64) - 1

_RE_COMMENT = re.compile(r"(#|;|//).*?$")
_RE_LABEL = re.compile(r"^\s*([A-Za-z_.$][\w.$]*):\s*$")


def _strip_comments(line: str) -> str:
    return _RE_COMMENT.sub("", line).strip()


def _detect_syntax(asm: str) -> str:
    if re.search(r"[%]\w+", asm) or re.search(r"\$\-?0x[0-9a-fA-F]+|\$\-?\d+", asm):
        return "att"
    if re.search(r"\bPTR\b|\[[^\]]+\]", asm):
        return "intel"
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
    v = int(s, base)
    return -v if neg else v


def _norm_reg(r: str) -> str:
    return r.strip().lstrip("%").lower()


def _split_operands(ops: str) -> List[str]:
    out: List[str] = []
    cur: List[str] = []
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


def _parse_att_mem(op: str) -> Optional[Tuple[int, Optional[str], Optional[str], int]]:
    # disp(base,index,scale)
    m = re.fullmatch(r"(?P<disp>[-+]?0x[0-9a-fA-F]+|[-+]?\d+)?\((?P<body>[^)]*)\)", op.strip())
    if not m:
        return None
    disp = _parse_int(m.group("disp") or "0") or 0
    body = m.group("body").strip()
    parts = [p.strip() for p in body.split(",")] if body else []
    base = _norm_reg(parts[0]) if len(parts) >= 1 and parts[0] else None
    index = _norm_reg(parts[1]) if len(parts) >= 2 and parts[1] else None
    scale = _parse_int(parts[2]) if len(parts) >= 3 and parts[2] else None
    sc = int(scale) if scale is not None else 1
    if sc not in (1, 2, 4, 8):
        sc = 1
    return disp, base, index, sc


def _parse_intel_mem(op: str) -> Optional[Tuple[int, Optional[str], Optional[str], int]]:
    s = op.strip()
    m_size = re.match(r"^(byte|word|dword|qword)\s+ptr\s+(?P<rest>.+)$", s, flags=re.IGNORECASE)
    if m_size:
        s = m_size.group("rest").strip()
    m = re.fullmatch(r"\[(?P<body>[^\]]+)\]", s)
    if not m:
        return None
    body = m.group("body").strip().replace(" ", "")
    tokens = re.split(r"(\+|\-)", body)
    sign = +1
    disp = 0
    base = None
    index = None
    scale = 1
    for t in tokens:
        if t == "+":
            sign = +1
            continue
        if t == "-":
            sign = -1
            continue
        if not t:
            continue
        m_is = re.fullmatch(r"([A-Za-z][\w]*)\*(\d+)", t)
        if m_is:
            idx = _norm_reg(m_is.group(1))
            sc = int(m_is.group(2))
            if sc in (1, 2, 4, 8) and index is None:
                index, scale = idx, sc
                continue
            return None
        if re.fullmatch(r"[A-Za-z][\w]*", t):
            reg = _norm_reg(t)
            if base is None:
                base = reg
            elif index is None:
                index, scale = reg, 1
            else:
                return None
            continue
        iv = _parse_int(t)
        if iv is not None:
            disp += sign * iv
            continue
        return None
    return disp, base, index, scale


def _eval_mem_addr(op: str, syntax: str, regs: Dict[str, int]) -> Optional[int]:
    if syntax == "att":
        parsed = _parse_att_mem(op)
    else:
        parsed = _parse_intel_mem(op)
    if not parsed:
        return None
    disp, base, index, scale = parsed
    addr = disp
    if base:
        addr += int(regs.get(base, 0))
    if index:
        addr += int(regs.get(index, 0)) * int(scale)
    return addr & MASK64


def _eval_operand_value(op: str, syntax: str, regs: Dict[str, int], mem: Dict[int, int]) -> Tuple[Optional[int], Optional[str]]:
    s = op.strip().rstrip(",").strip()
    if not s:
        return None, "empty operand"

    if syntax == "att":
        if s.startswith("$"):
            iv = _parse_int(s[1:])
            return (iv & MASK64) if iv is not None else None, None if iv is not None else f"bad immediate: {s}"
        if s.startswith("%"):
            return int(regs.get(_norm_reg(s), 0)) & MASK64, None
        addr = _eval_mem_addr(s, syntax, regs)
        if addr is not None:
            return int(mem.get(addr, 0)) & MASK64, None
        iv = _parse_int(s)
        if iv is not None:
            return iv & MASK64, None
        return None, f"unknown operand: {s}"

    # intel
    if re.search(r"\bptr\b", s, flags=re.IGNORECASE) or (s.startswith("[") and s.endswith("]")):
        addr = _eval_mem_addr(s, syntax, regs)
        if addr is None:
            return None, f"bad memory operand: {s}"
        return int(mem.get(addr, 0)) & MASK64, None
    if re.fullmatch(r"[-+]?0x[0-9a-fA-F]+|[-+]?\d+", s):
        iv = _parse_int(s)
        return (iv & MASK64) if iv is not None else None, None if iv is not None else f"bad immediate: {s}"
    if re.fullmatch(r"[A-Za-z][\w]*", s):
        return int(regs.get(_norm_reg(s), 0)) & MASK64, None
    return None, f"unknown operand: {s}"


def _write_operand(op: str, syntax: str, regs: Dict[str, int], mem: Dict[int, int], value: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    s = op.strip().rstrip(",").strip()
    value &= MASK64

    if syntax == "att":
        if s.startswith("%"):
            reg = _norm_reg(s)
            regs[reg] = value
            return {"kind": "reg", "reg": reg, "value": value}, None
        addr = _eval_mem_addr(s, syntax, regs)
        if addr is not None:
            mem[addr] = value
            return {"kind": "mem", "addr": addr, "value": value}, None
        return None, f"unsupported destination: {s}"

    # intel
    if re.search(r"\bptr\b", s, flags=re.IGNORECASE) or (s.startswith("[") and s.endswith("]")):
        addr = _eval_mem_addr(s, syntax, regs)
        if addr is None:
            return None, f"bad destination mem: {s}"
        mem[addr] = value
        return {"kind": "mem", "addr": addr, "value": value}, None
    if re.fullmatch(r"[A-Za-z][\w]*", s):
        reg = _norm_reg(s)
        regs[reg] = value
        return {"kind": "reg", "reg": reg, "value": value}, None
    return None, f"unsupported destination: {s}"


def _snapshot(regs: Dict[str, int], mem: Dict[int, int]) -> Dict[str, Any]:
    return {"regs": dict(regs), "mem": dict(mem)}


def _diff(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    b_regs = before["regs"]
    a_regs = after["regs"]
    reg_changes = {k: a_regs[k] for k in a_regs if b_regs.get(k) != a_regs.get(k)}

    b_mem = before["mem"]
    a_mem = after["mem"]
    mem_changes = {k: a_mem[k] for k in a_mem if b_mem.get(k) != a_mem.get(k)}
    return {"regs": reg_changes, "mem": mem_changes}


def _parse_line_to_instr(line: str) -> Optional[Dict[str, Any]]:
    stripped = _strip_comments(line)
    if not stripped:
        return None
    if _RE_LABEL.match(stripped):
        return None
    parts = stripped.split(None, 1)
    mnemonic = parts[0].lower()
    ops_s = parts[1] if len(parts) > 1 else ""
    ops = _split_operands(ops_s) if ops_s else []
    return {"mnemonic": mnemonic, "operands": ops, "raw": line}


def _normalize_two_operands(ops: List[str], syntax: str) -> Tuple[Optional[str], Optional[str]]:
    if len(ops) != 2:
        return None, None
    if syntax == "att":
        return ops[0], ops[1]  # src, dst
    return ops[1], ops[0]  # src, dst for intel (dst,src in text)


def run(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trace a subset of x86-64 assembly.

    See skills.md for the supported input/output schema.
    """
    asm = (input or {}).get("asm")
    if not isinstance(asm, str) or not asm.strip():
        return {"ok": False, "syntax": None, "steps": [], "final_state": {}, "warnings": [], "errors": ["Missing required string input['asm']."]}

    syntax_req = (input or {}).get("syntax", "auto")
    syntax = _detect_syntax(asm) if syntax_req == "auto" else str(syntax_req).lower()
    if syntax not in ("att", "intel"):
        syntax = _detect_syntax(asm)

    initial_state = (input or {}).get("initial_state", {}) or {}
    regs: Dict[str, int] = {k.lower(): int(v) & MASK64 for k, v in (initial_state.get("regs", {}) or {}).items()}
    mem: Dict[int, int] = {int(k) & MASK64: int(v) & MASK64 for k, v in (initial_state.get("mem", {}) or {}).items()}

    # Provide default stack pointer if missing to keep examples usable.
    regs.setdefault("rsp", 0x0)
    regs.setdefault("rbp", 0x0)

    max_steps = int((input or {}).get("max_steps", 200))
    if max_steps <= 0:
        max_steps = 200
    stop_on_error = bool((input or {}).get("stop_on_error", True))

    warnings: List[str] = []
    errors: List[str] = []
    steps: List[Dict[str, Any]] = []

    lines = asm.splitlines()
    ip = 0
    executed = 0

    for raw in lines:
        if executed >= max_steps:
            warnings.append(f"Stopped after {max_steps} steps (max_steps cap).")
            break
        instr = _parse_line_to_instr(raw)
        if instr is None:
            continue

        before = _snapshot(regs, mem)
        mnem = instr["mnemonic"]
        ops = instr["operands"]

        err: Optional[str] = None
        mem_write: Optional[Dict[str, Any]] = None

        try:
            if mnem in ("mov", "movq", "movl", "movb", "movw", "lea", "add", "addq", "sub", "subq", "xor", "xorq", "and", "or", "imul"):
                if len(ops) != 2:
                    err = f"{mnem} expects 2 operands, got {len(ops)}"
                else:
                    src_txt, dst_txt = _normalize_two_operands(ops, syntax)
                    if src_txt is None or dst_txt is None:
                        err = "bad operand normalization"
                    else:
                        if mnem == "lea":
                            addr = _eval_mem_addr(src_txt, syntax, regs)
                            if addr is None:
                                err = f"lea source not recognized as mem addr: {src_txt}"
                            else:
                                mem_write, err = _write_operand(dst_txt, syntax, regs, mem, addr)
                        else:
                            src_val, e1 = _eval_operand_value(src_txt, syntax, regs, mem)
                            if e1:
                                err = e1
                            else:
                                if mnem.startswith("mov"):
                                    mem_write, err = _write_operand(dst_txt, syntax, regs, mem, int(src_val or 0))
                                elif mnem.startswith("add"):
                                    dst_val, e2 = _eval_operand_value(dst_txt, syntax, regs, mem)
                                    if e2:
                                        err = e2
                                    else:
                                        mem_write, err = _write_operand(dst_txt, syntax, regs, mem, (int(dst_val or 0) + int(src_val or 0)) & MASK64)
                                elif mnem.startswith("sub"):
                                    dst_val, e2 = _eval_operand_value(dst_txt, syntax, regs, mem)
                                    if e2:
                                        err = e2
                                    else:
                                        mem_write, err = _write_operand(dst_txt, syntax, regs, mem, (int(dst_val or 0) - int(src_val or 0)) & MASK64)
                                elif mnem.startswith("xor"):
                                    dst_val, e2 = _eval_operand_value(dst_txt, syntax, regs, mem)
                                    if e2:
                                        err = e2
                                    else:
                                        mem_write, err = _write_operand(dst_txt, syntax, regs, mem, (int(dst_val or 0) ^ int(src_val or 0)) & MASK64)
                                elif mnem == "and":
                                    dst_val, e2 = _eval_operand_value(dst_txt, syntax, regs, mem)
                                    if e2:
                                        err = e2
                                    else:
                                        mem_write, err = _write_operand(dst_txt, syntax, regs, mem, (int(dst_val or 0) & int(src_val or 0)) & MASK64)
                                elif mnem == "or":
                                    dst_val, e2 = _eval_operand_value(dst_txt, syntax, regs, mem)
                                    if e2:
                                        err = e2
                                    else:
                                        mem_write, err = _write_operand(dst_txt, syntax, regs, mem, (int(dst_val or 0) | int(src_val or 0)) & MASK64)
                                elif mnem == "imul":
                                    dst_val, e2 = _eval_operand_value(dst_txt, syntax, regs, mem)
                                    if e2:
                                        err = e2
                                    else:
                                        mem_write, err = _write_operand(dst_txt, syntax, regs, mem, (int(dst_val or 0) * int(src_val or 0)) & MASK64)
                                else:
                                    err = f"unhandled ALU op: {mnem}"

            elif mnem == "push":
                if len(ops) != 1:
                    err = f"push expects 1 operand, got {len(ops)}"
                else:
                    val, e = _eval_operand_value(ops[0], syntax, regs, mem)
                    if e:
                        err = e
                    else:
                        regs["rsp"] = (int(regs.get("rsp", 0)) - 8) & MASK64
                        mem[int(regs["rsp"])] = int(val or 0) & MASK64
                        mem_write = {"kind": "mem", "addr": int(regs["rsp"]), "value": mem[int(regs["rsp"])]}

            elif mnem == "pop":
                if len(ops) != 1:
                    err = f"pop expects 1 operand, got {len(ops)}"
                else:
                    addr = int(regs.get("rsp", 0)) & MASK64
                    val = int(mem.get(addr, 0)) & MASK64
                    mem_write, err = _write_operand(ops[0], syntax, regs, mem, val)
                    regs["rsp"] = (addr + 8) & MASK64

            elif mnem in ("ret", "retq"):
                # Model as popping return address into a pseudo-reg 'rip' (if present).
                addr = int(regs.get("rsp", 0)) & MASK64
                ret_addr = int(mem.get(addr, 0)) & MASK64
                regs["rsp"] = (addr + 8) & MASK64
                regs["rip"] = ret_addr

            elif mnem == "call":
                # Without symbol resolution, we just push a placeholder "return address".
                regs["rsp"] = (int(regs.get("rsp", 0)) - 8) & MASK64
                mem[int(regs["rsp"])] = 0xDEADBEEFDEADBEEF
                warnings.append("call: pushed placeholder return address; did not jump to target.")

            elif mnem in ("cmp", "test", "jne", "je", "jg", "jge", "jl", "jle", "jmp"):
                # Flags/control flow not modeled; record as warning.
                warnings.append(f"{mnem}: flags/control-flow not modeled; trace continues linearly.")

            else:
                err = f"Unsupported instruction mnemonic: {mnem}"

        except Exception as ex:  # pragma: no cover
            err = f"Exception executing '{mnem}': {ex}"

        after = _snapshot(regs, mem)
        d = _diff(before, after)

        step = {
            "ip": ip,
            "asm": raw,
            "instruction": {"mnemonic": mnem, "operands": ops, "syntax": syntax},
            "before": {"regs": before["regs"]},
            "after": {"regs": after["regs"]},
            "diff": d,
        }
        if mem_write:
            step["mem_write"] = mem_write
        if err:
            step["error"] = err
            errors.append(err)
            steps.append(step)
            if stop_on_error:
                break
        else:
            steps.append(step)

        ip += 1
        executed += 1

    return {
        "ok": len(errors) == 0,
        "syntax": syntax,
        "steps": steps,
        "final_state": {"regs": dict(regs), "mem": dict(mem)},
        "warnings": warnings,
        "errors": errors,
    }