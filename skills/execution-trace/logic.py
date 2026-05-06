"""Tiny step tracer: Intel-style mov/add/sub/push/pop on 64-bit regs + qword memory.

Outputs are tutoring-oriented: each step includes a compact "delta" describing what changed,
so a chatbot can guide a student step-by-step while tracking registers/memory.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

MASK = (1 << 64) - 1


def _norm(r: str) -> str:
    return r.strip().lower()


def _hex(v: int) -> str:
    return hex(int(v) & MASK)


def _delta(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    bregs = (before.get("regs") or {}) if isinstance(before.get("regs"), dict) else {}
    aregs = (after.get("regs") or {}) if isinstance(after.get("regs"), dict) else {}
    bmem = (before.get("mem") or {}) if isinstance(before.get("mem"), dict) else {}
    amem = (after.get("mem") or {}) if isinstance(after.get("mem"), dict) else {}

    changed_regs: Dict[str, Dict[str, str]] = {}
    for k in set(bregs.keys()) | set(aregs.keys()):
        bv = bregs.get(k)
        av = aregs.get(k)
        if bv != av and isinstance(av, int):
            changed_regs[str(k)] = {"before": _hex(int(bv) if isinstance(bv, int) else 0), "after": _hex(int(av))}

    touched_mem: Dict[str, Dict[str, str]] = {}
    for k in set(bmem.keys()) | set(amem.keys()):
        bv = bmem.get(k)
        av = amem.get(k)
        if bv != av and isinstance(k, int) and isinstance(av, int):
            touched_mem[_hex(int(k))] = {"before": _hex(int(bv) if isinstance(bv, int) else 0), "after": _hex(int(av))}

    return {"regs_changed": changed_regs, "mem_changed": touched_mem}


def _delta_summary(d: Dict[str, Any], *, max_regs: int = 4) -> str:
    regs = d.get("regs_changed") or {}
    if not isinstance(regs, dict) or not regs:
        return "(no register change)"

    priority = [
        "rax",
        "eax",
        "rbx",
        "rcx",
        "rdx",
        "rsi",
        "rdi",
        "rsp",
        "rbp",
        "r8",
        "r9",
        "r10",
        "r11",
        "r12",
        "r13",
        "r14",
        "r15",
    ]
    keys = list(regs.keys())
    keys.sort(key=lambda k: (priority.index(k) if k in priority else 999, k))

    parts: List[str] = []
    for k in keys[:max_regs]:
        v = regs.get(k) or {}
        if isinstance(v, dict):
            parts.append(f"{k}: {v.get('before')}→{v.get('after')}")
    extra = len(keys) - len(parts)
    if extra > 0:
        parts.append(f"+{extra} more")
    return ", ".join(parts)


def _reg_hex(regs: Dict[str, Any], name: str) -> str:
    v = regs.get(name)
    if isinstance(v, int):
        return _hex(v)
    return ""


def _walkthrough_table_md(steps: List[Dict[str, Any]], *, max_steps: int = 12) -> str:
    """
    A compact markdown table so a tutor can point at Step N and track values.
    """
    if not steps:
        return ""
    cols = ["step", "asm", "delta", "rdi", "rsi", "rdx", "rax", "rsp"]
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for i, st in enumerate(steps[:max_steps]):
        asm = str((st.get("asm") or "")).strip().split("\n")[0]
        delta = str(st.get("delta_summary") or "")
        after_regs = ((st.get("after") or {}).get("regs") or {}) if isinstance(st.get("after"), dict) else {}
        if not isinstance(after_regs, dict):
            after_regs = {}
        row = [
            str(i),
            asm.replace("|", "\\|"),
            delta.replace("|", "\\|"),
            _reg_hex(after_regs, "rdi"),
            _reg_hex(after_regs, "rsi"),
            _reg_hex(after_regs, "rdx"),
            _reg_hex(after_regs, "rax"),
            _reg_hex(after_regs, "rsp"),
        ]
        lines.append("| " + " | ".join(row) + " |")
    if len(steps) > max_steps:
        lines.append(f"\n… ({len(steps) - max_steps} more steps not shown) …")
    return "\n".join(lines)


def _parse_mem(s: str) -> Optional[Tuple[int, str]]:
    s = s.strip()
    m = re.match(r"qword\s+ptr\s+\[(.+)\]", s, re.I)
    if not m:
        m = re.match(r"\[(.+)\]", s)
    if not m:
        return None
    body = m.group(1).replace(" ", "")
    if re.fullmatch(r"[a-z0-9]+", body, re.I):
        return 0, _norm(body)
    m2 = re.match(r"([a-z0-9]+)([+-]\d+)", body, re.I)
    if m2:
        return int(m2.group(2)), _norm(m2.group(1))
    return None


def _read_op(op: str, regs: Dict[str, int], mem: Dict[int, int]) -> int:
    op = op.strip().rstrip(",").strip()
    if re.fullmatch(r"-?0x[0-9a-f]+|-?\d+", op, re.I):
        return int(op, 0) & MASK
    if op.startswith("QWORD") or op.startswith("["):
        p = _parse_mem(op)
        if not p:
            return 0
        disp, base = p
        addr = (regs.get(base, 0) + disp) & MASK
        return mem.get(addr, 0) & MASK
    return regs.get(_norm(op), 0) & MASK


def _write_op(op: str, val: int, regs: Dict[str, int], mem: Dict[int, int]) -> None:
    op = op.strip().rstrip(",").strip()
    val &= MASK
    if op.startswith("QWORD") or op.startswith("["):
        p = _parse_mem(op)
        if p:
            disp, base = p
            addr = (regs.get(base, 0) + disp) & MASK
            mem[addr] = val
        return
    regs[_norm(op)] = val


def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    asm = (inp or {}).get("asm")
    if not isinstance(asm, str) or not asm.strip():
        return {"ok": False, "steps": [], "final_state": {}, "errors": ["Missing input['asm']."]}

    st = (inp or {}).get("initial_state") or {}
    regs = {k.lower(): int(v) & MASK for k, v in (st.get("regs") or {}).items()}
    mem = {int(a) & MASK: int(v) & MASK for a, v in (st.get("mem") or {}).items()}
    regs.setdefault("rsp", 0x1000)
    regs.setdefault("rbp", 0)

    steps: List[Dict[str, Any]] = []
    for raw in asm.splitlines():
        line = raw.split("#", 1)[0].split(";", 1)[0].strip()
        if not line or line.endswith(":"):
            continue
        before = {"regs": dict(regs), "mem": dict(mem)}
        parts = line.split(None, 1)
        mn = parts[0].lower()
        rest = parts[1] if len(parts) > 1 else ""
        ops = [x.strip() for x in rest.split(",")] if rest else []

        err = None
        if mn == "mov" and len(ops) == 2:
            _write_op(ops[0], _read_op(ops[1], regs, mem), regs, mem)
        elif mn == "add" and len(ops) == 2:
            dst, src = ops[0], ops[1]
            _write_op(dst, _read_op(dst, regs, mem) + _read_op(src, regs, mem), regs, mem)
        elif mn == "sub" and len(ops) == 2:
            dst, src = ops[0], ops[1]
            _write_op(dst, _read_op(dst, regs, mem) - _read_op(src, regs, mem), regs, mem)
        elif mn == "push" and len(ops) == 1:
            regs["rsp"] = (regs["rsp"] - 8) & MASK
            mem[regs["rsp"]] = _read_op(ops[0], regs, mem)
        elif mn == "pop" and len(ops) == 1:
            v = mem.get(regs["rsp"], 0)
            regs["rsp"] = (regs["rsp"] + 8) & MASK
            _write_op(ops[0], v, regs, mem)
        else:
            err = f"unsupported: {mn}"

        after = {"regs": dict(regs), "mem": dict(mem)}
        d = _delta(before, after)
        steps.append(
            {
                "asm": raw,
                "error": err,
                "before": before,
                "after": after,
                "delta": d,
                "delta_summary": _delta_summary(d),
            }
        )
        if err:
            return {
                "ok": False,
                "steps": steps,
                "walkthrough_table_md": _walkthrough_table_md(steps),
                "final_state": after,
                "errors": [err],
            }

    return {
        "ok": True,
        "steps": steps,
        "walkthrough_table_md": _walkthrough_table_md(steps),
        "final_state": {"regs": regs, "mem": mem},
        "errors": [],
    }
