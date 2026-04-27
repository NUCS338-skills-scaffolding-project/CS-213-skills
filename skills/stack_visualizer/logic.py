from __future__ import annotations

from typing import Any, Dict, List, Optional


MASK64 = (1 << 64) - 1


def _as_int(x: Any) -> Optional[int]:
    try:
        return int(x)
    except Exception:
        return None


def _guess_label(addr: int, rbp: Optional[int]) -> Optional[str]:
    if rbp is None:
        return None
    if addr == rbp:
        return "saved_rbp"
    if addr == rbp + 8:
        return "return_address"
    if addr < rbp:
        off = addr - rbp
        return f"local[{off}]"
    if addr > rbp + 8:
        off = addr - rbp
        return f"caller[{off}]"
    return None


def run(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a simple stack visualization from registers + a qword memory map.

    Expected input keys:
      - regs: dict with at least rsp (rbp recommended)
      - mem: dict[int,int] mapping address->qword (optional)
      - word_size: slot size in bytes (default 8)
      - max_slots: cap number of slots returned (default 64)
      - label_hints: dict[int,str] explicit labels (optional)
    """
    regs = (input or {}).get("regs")
    if not isinstance(regs, dict):
        return {"ok": False, "frame": {}, "slots": [], "warnings": [], "errors": ["Missing required dict input['regs']."]}

    rsp = _as_int(regs.get("rsp"))
    rbp = _as_int(regs.get("rbp")) if "rbp" in regs else None
    if rsp is None:
        return {"ok": False, "frame": {}, "slots": [], "warnings": [], "errors": ["regs must include integer 'rsp'."]}

    mem_in = (input or {}).get("mem", {}) or {}
    if not isinstance(mem_in, dict):
        mem_in = {}
    mem: Dict[int, int] = {int(k) & MASK64: int(v) & MASK64 for k, v in mem_in.items()}

    word_size = int((input or {}).get("word_size", 8))
    if word_size not in (1, 2, 4, 8, 16):
        word_size = 8
    max_slots = int((input or {}).get("max_slots", 64))
    if max_slots <= 0:
        max_slots = 64
    label_hints = (input or {}).get("label_hints", {}) or {}
    if not isinstance(label_hints, dict):
        label_hints = {}

    warnings: List[str] = []
    errors: List[str] = []

    # Determine window bounds.
    # If rbp looks valid and above rsp, show rsp..rbp+16 (saved rbp + retaddr) window.
    # Otherwise, show a small window above rsp.
    rbp_valid = rbp is not None and rbp != 0 and rbp >= rsp and (rbp - rsp) <= (max_slots * word_size)
    if not rbp_valid:
        if rbp is None or rbp == 0:
            warnings.append("rbp missing/zero; showing stack window relative to rsp only.")
        else:
            warnings.append("rbp not within expected range above rsp; showing stack window relative to rsp only.")
        lo = rsp
        hi = (rsp + (max_slots - 1) * word_size) & MASK64
        rbp_for_offsets: Optional[int] = None
    else:
        lo = rsp
        hi = rbp + 16
        rbp_for_offsets = rbp

    # Build slots at word_size increments.
    slots: List[Dict[str, Any]] = []
    addr = lo
    count = 0
    while True:
        if count >= max_slots:
            warnings.append(f"Slot output capped at max_slots={max_slots}.")
            break
        if (rbp_valid and addr > hi) or (not rbp_valid and count >= max_slots):
            break

        value = mem.get(addr)
        label = label_hints.get(addr)
        if label is None:
            label = _guess_label(addr, rbp_for_offsets)

        offset_from_rbp = (addr - rbp_for_offsets) if rbp_for_offsets is not None else None
        slots.append(
            {
                "addr": addr,
                "offset_from_rbp": offset_from_rbp,
                "value": value,
                "label": label,
            }
        )

        addr = (addr + word_size) & MASK64
        count += 1
        if rbp_valid and addr > hi:
            break

    frame = {"rsp": rsp, "rbp": rbp, "word_size": word_size, "lo": lo, "hi": hi}
    return {"ok": len(errors) == 0, "frame": frame, "slots": slots, "warnings": warnings, "errors": errors}