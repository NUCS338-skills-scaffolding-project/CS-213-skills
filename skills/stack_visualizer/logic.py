"""Stack slots from rsp/rbp + qword memory (snapshot only)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

MASK = (1 << 64) - 1


def _guess(addr: int, rbp: Optional[int]) -> Optional[str]:
    if rbp is None:
        return None
    if addr == rbp:
        return "saved_rbp"
    if addr == rbp + 8:
        return "return_address"
    if addr < rbp:
        return f"local[{addr - rbp}]"
    return None


def _hex(v: int) -> str:
    return hex(int(v) & MASK)


def _stack_table_md(frame: Dict[str, Any], slots: List[Dict[str, Any]]) -> str:
    rsp = frame.get("rsp")
    rbp = frame.get("rbp")
    rows: List[str] = [
        "| addr | rbp_off | label | value |",
        "| --- | --- | --- | --- |",
    ]
    for sl in slots[:32]:
        addr = sl.get("addr")
        off = sl.get("offset_from_rbp")
        lab = sl.get("label") or ""
        val = sl.get("value")
        addr_s = _hex(addr) if isinstance(addr, int) else str(addr)
        off_s = str(off) if off is not None else ""
        val_s = _hex(val) if isinstance(val, int) else ""

        # Small marker for rsp/rbp rows so the tutor can point at them.
        if isinstance(addr, int) and isinstance(rsp, int) and addr == rsp:
            lab = (lab + " " if lab else "") + "<- rsp"
        if isinstance(addr, int) and isinstance(rbp, int) and addr == rbp:
            lab = (lab + " " if lab else "") + "<- rbp"

        rows.append(f"| {addr_s} | {off_s} | {str(lab).replace('|','\\\\|')} | {val_s} |")
    if len(slots) > 32:
        rows.append(f"\n… ({len(slots) - 32} more slots not shown) …")
    return "\n".join(rows)


def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    inp = inp or {}
    regs = inp.get("regs")
    if not isinstance(regs, dict):
        return {"ok": False, "frame": {}, "slots": [], "errors": ["Need input['regs'] (dict with at least rsp)."]}

    rsp = regs.get("rsp")
    try:
        rsp = int(rsp) & MASK
    except Exception:
        return {"ok": False, "frame": {}, "slots": [], "errors": ["regs['rsp'] must be an integer."]}

    rbp = regs.get("rbp")
    try:
        rbp_i = int(rbp) & MASK if rbp is not None else None
    except Exception:
        rbp_i = None

    mem_in = inp.get("mem") or {}
    mem = {}
    if isinstance(mem_in, dict):
        for k, v in mem_in.items():
            try:
                mem[int(k) & MASK] = int(v) & MASK
            except Exception:
                pass

    ws = int(inp.get("word_size", 8) or 8)
    if ws not in (1, 2, 4, 8):
        ws = 8
    max_slots = min(int(inp.get("max_slots", 32) or 32), 64)
    hints = inp.get("label_hints") or {}
    if not isinstance(hints, dict):
        hints = {}

    use_rbp = rbp_i is not None and rbp_i != 0 and rbp_i >= rsp
    hi = (rbp_i + 16) & MASK if use_rbp else (rsp + (max_slots - 1) * ws) & MASK
    rbp_off = rbp_i if use_rbp else None
    warnings: List[str] = []
    if not use_rbp:
        warnings.append("Using rsp-only window (rbp missing or not above rsp).")

    slots: List[Dict[str, Any]] = []
    addr = rsp
    for _ in range(max_slots):
        if use_rbp and addr > hi:
            break
        lab = hints.get(addr) or _guess(addr, rbp_off)
        slots.append(
            {
                "addr": addr,
                "offset_from_rbp": (addr - rbp_off) if rbp_off is not None else None,
                "value": mem.get(addr),
                "label": lab,
            }
        )
        addr = (addr + ws) & MASK
        if not use_rbp and len(slots) >= max_slots:
            break

    frame = {"rsp": rsp, "rbp": rbp_i, "word_size": ws}
    return {
        "ok": True,
        "frame": frame,
        "slots": slots,
        "table_md": _stack_table_md(frame, slots),
        "warnings": warnings,
        "errors": [],
    }
