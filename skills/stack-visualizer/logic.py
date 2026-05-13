"""Stack-focused views: snapshot around rsp/rbp, or asm-driven timeline of rsp + stack memory.

Use ``student_mode=True`` when tutoring so numeric rsp trajectories and cell values are not leaked;
the same simulation still runs internally to validate supported instructions.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

MASK = (1 << 64) - 1


def _norm(r: str) -> str:
    return r.strip().lower()


def _hex(v: int) -> str:
    return hex(int(v) & MASK)


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
    if op.upper().startswith("QWORD") or op.startswith("["):
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
    if op.upper().startswith("QWORD") or op.startswith("["):
        p = _parse_mem(op)
        if p:
            disp, base = p
            addr = (regs.get(base, 0) + disp) & MASK
            mem[addr] = val
        return
    regs[_norm(op)] = val


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

        if isinstance(addr, int) and isinstance(rsp, int) and addr == rsp:
            lab = (lab + " " if lab else "") + "<- rsp"
        if isinstance(addr, int) and isinstance(rbp, int) and addr == rbp:
            lab = (lab + " " if lab else "") + "<- rbp"

        rows.append(f"| {addr_s} | {off_s} | {str(lab).replace('|','\\\\|')} | {val_s} |")
    if len(slots) > 32:
        rows.append(f"\n… ({len(slots) - 32} more slots not shown) …")
    return "\n".join(rows)


def _build_slots(
    rsp: int,
    rbp_i: Optional[int],
    mem: Dict[int, int],
    *,
    word_size: int,
    max_slots: int,
    label_hints: Dict[Any, Any],
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[str]]:
    ws = word_size
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
        lab = label_hints.get(addr) if isinstance(label_hints, dict) else None
        if lab is None:
            lab = _guess(addr, rbp_off)
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
    return frame, slots, warnings


def _regs_mem_from_inp(inp: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[int, int]]:
    inp = inp or {}
    if isinstance(inp.get("initial_state"), dict):
        st = inp["initial_state"]
        regs_raw = st.get("regs") or {}
        mem_in = st.get("mem") or {}
    else:
        regs_raw = inp.get("regs") or {}
        mem_in = inp.get("mem") or {}

    if not isinstance(regs_raw, dict):
        regs_raw = {}
    regs: Dict[str, int] = {}
    for k, v in regs_raw.items():
        try:
            regs[str(k).lower()] = int(v) & MASK
        except Exception:
            continue

    mem: Dict[int, int] = {}
    if isinstance(mem_in, dict):
        for k, v in mem_in.items():
            try:
                mem[int(k) & MASK] = int(v) & MASK
            except Exception:
                pass
    return regs, mem


def _pedagogy_meta(*, student_mode: bool) -> Dict[str, Any]:
    return {
        "intent": "stack_visualizer_hints" if student_mode else "stack_visualizer_full",
        "hints_only": bool(student_mode),
        "note": (
            "Questions about rsp movement and stack slots — no numeric solution trace. "
            "Have the student predict, then optionally rerun with student_mode=false to verify."
            if student_mode
            else "Contains concrete rsp addresses and memory values — do not paste the full timeline as a finished answer; "
            "prefer one instruction at a time or student_mode for learners."
        ),
    }


def _rsp_imm_adjust(mn: str, ops: List[str]) -> Optional[int]:
    """If insn adjusts rsp by an immediate, return signed delta (negative = grow stack)."""
    if len(ops) != 2:
        return None
    dst, src = ops[0], ops[1]
    if _norm(dst) != "rsp":
        return None
    if not re.fullmatch(r"-?0x[0-9a-f]+|-?\d+", src.strip(), re.I):
        return None
    imm = int(src.strip(), 0) & MASK
    if mn == "sub":
        return -imm
    if mn == "add":
        return imm
    return None


def _operand_mentions_rsp(op: str) -> bool:
    return "rsp" in op.lower()


def _stack_instruction_hints(mn: str, ops: List[str]) -> Dict[str, Any]:
    mn = mn.lower()
    roles: List[str] = []
    questions: List[str] = []
    hints: List[str] = []

    if mn == "push" and len(ops) == 1:
        roles.append("Decrements rsp (in this ABI) and stores the pushed operand’s value to memory at the new top of stack.")
        questions.append("By how many bytes does rsp move on a 64-bit push, and toward lower or higher addresses?")
        questions.append("After rsp moves, where (relative to the new rsp) is the qword written?")
        hints.append("Name the source register or immediate before worrying about the exact hex in memory.")
    elif mn == "pop" and len(ops) == 1:
        roles.append("Loads a qword from [rsp] into the destination, then increases rsp.")
        questions.append("Which address is read first — rsp before or after it changes?")
        hints.append("Think about whether pop grows rsp toward larger addresses and by how many bytes.")
    elif mn in ("sub", "add") and _rsp_imm_adjust(mn, ops) is not None:
        roles.append("Adjusts rsp by an immediate (common for stack allocation / cleanup).")
        questions.append("Is rsp moving into unused stack space or back toward the caller’s area? How many bytes?")
    elif mn == "mov" and len(ops) == 2 and (_operand_mentions_rsp(ops[0]) or _operand_mentions_rsp(ops[1])):
        roles.append("May load or store through an address that depends on rsp.")
        questions.append("Is rsp used as a base for addressing? What displacement (if any) is added?")
        hints.append("Separate ‘address arithmetic’ from ‘value moved’: first resolve where the qword lives.")
    else:
        roles.append("May not change rsp; still check if memory operands use rsp-relative addressing.")
        questions.append("Does this instruction read or write any qword whose address is built from rsp?")

    return {"stack_roles": roles, "questions": questions, "hints": hints}


def _visualization_template_md(*, num_slots: int = 6) -> str:
    rows = ["| slot index (0 = rsp) | byte offset from rsp | value (you fill) |", "| --- | --- | --- |"]
    for i in range(num_slots):
        rows.append(f"| {i} | {i * 8} | ? |")
    return "\n".join(rows) + "\n\nFill values only after you predict rsp and what each instruction does."


def _run_asm_timeline(inp: Dict[str, Any]) -> Dict[str, Any]:
    student_mode = bool(inp.get("student_mode"))
    asm = inp.get("asm")
    if not isinstance(asm, str) or not asm.strip():
        return {"ok": False, "pedagogy": _pedagogy_meta(student_mode=student_mode), "errors": ["Missing or empty input['asm'] for timeline mode."]}

    regs, mem = _regs_mem_from_inp(inp)
    if "rsp" not in regs:
        return {
            "ok": False,
            "pedagogy": _pedagogy_meta(student_mode=student_mode),
            "errors": [
                "Assembly timeline requires an initial stack pointer: set regs['rsp'] (or initial_state.regs['rsp']).",
            ],
        }

    ws = int(inp.get("word_size", 8) or 8)
    if ws not in (1, 2, 4, 8):
        ws = 8
    max_slots = min(int(inp.get("max_slots", 16) or 16), 64)
    max_steps = min(int(inp.get("max_steps", 200) or 200), 500)
    hints_in = inp.get("label_hints") or {}
    if not isinstance(hints_in, dict):
        hints_in = {}

    regs.setdefault("rbp", 0)
    rbp_i: Optional[int] = regs.get("rbp") if regs.get("rbp", 0) != 0 else None
    if rbp_i is not None:
        rbp_i = int(rbp_i) & MASK

    timeline: List[Dict[str, Any]] = []
    timeline_hints: List[Dict[str, Any]] = []
    step_idx = 0
    lines_seen = 0

    for raw in asm.splitlines():
        if lines_seen >= max_steps:
            break
        line = raw.split("#", 1)[0].split(";", 1)[0].strip()
        if not line or line.endswith(":"):
            continue
        lines_seen += 1

        parts = line.split(None, 1)
        mn = parts[0].lower()
        rest = parts[1] if len(parts) > 1 else ""
        ops = [x.strip() for x in rest.split(",")] if rest else []

        rsp_before = int(regs["rsp"]) & MASK
        mem_write: Optional[Dict[str, Any]] = None
        mem_note: Optional[str] = None

        err: Optional[str] = None
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
            waddr = regs["rsp"]
            mem[waddr] = _read_op(ops[0], regs, mem)
            mem_write = {"kind": "mem", "addr": waddr, "value": mem.get(waddr)}
        elif mn == "pop" and len(ops) == 1:
            r_at = rsp_before
            v = mem.get(r_at, 0)
            regs["rsp"] = (regs["rsp"] + 8) & MASK
            _write_op(ops[0], v, regs, mem)
            mem_note = f"Loaded qword from [{_hex(r_at)}] into destination; rsp increased by 8."
        else:
            err = f"unsupported: {mn}"

        rsp_after = int(regs["rsp"]) & MASK
        change: Dict[str, Any] = {
            "rsp_before": rsp_before,
            "rsp_after": rsp_after,
            "mem_write": mem_write,
            "mem_note": mem_note,
        }

        frame, slots, warnings = _build_slots(rsp_after, rbp_i, mem, word_size=ws, max_slots=max_slots, label_hints=hints_in)

        entry = {
            "step": step_idx,
            "asm": raw,
            "change": change,
            "slots": slots,
            "table_md": _stack_table_md(frame, slots),
            "warnings": warnings,
            "error": err,
        }
        timeline.append(entry)

        sh = _stack_instruction_hints(mn, ops)
        timeline_hints.append(
            {
                "step": step_idx,
                "asm": raw,
                "stack_roles": sh["stack_roles"],
                "questions": sh["questions"],
                "hints": sh["hints"],
                "error": err,
            }
        )

        step_idx += 1
        if err:
            out: Dict[str, Any] = {
                "ok": False,
                "pedagogy": _pedagogy_meta(student_mode=student_mode),
                "errors": [err],
            }
            if student_mode:
                out["timeline_hints"] = timeline_hints
                out["visualization_template_md"] = _visualization_template_md()
            else:
                out["timeline"] = timeline
            return out

    final_rsp = int(regs["rsp"]) & MASK
    final_frame, final_slots, final_warnings = _build_slots(
        final_rsp, rbp_i, mem, word_size=ws, max_slots=max_slots, label_hints=hints_in
    )

    base: Dict[str, Any] = {
        "ok": True,
        "pedagogy": _pedagogy_meta(student_mode=student_mode),
        "final_frame": {"rsp": final_rsp, "rbp": rbp_i, "word_size": ws},
        "final_slots": final_slots,
        "final_table_md": _stack_table_md({"rsp": final_rsp, "rbp": rbp_i, "word_size": ws}, final_slots),
        "final_warnings": final_warnings,
        "errors": [],
    }
    if student_mode:
        base["timeline_hints"] = timeline_hints
        base["visualization_template_md"] = _visualization_template_md(num_slots=min(8, max_slots))
        base["initialization_hints"] = [
            "You already fixed rsp — good. Before opening the full numeric trace, redraw the qwords above rsp after each push/pop yourself.",
            "Compare your predicted rsp movement to the *questions* in each step; only then rerun with student_mode=false to verify bytes.",
        ]
    else:
        base["timeline"] = timeline
    return base


def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    inp = inp or {}
    student_mode = bool(inp.get("student_mode"))
    asm = inp.get("asm")

    if isinstance(asm, str) and asm.strip():
        out = _run_asm_timeline(inp)
        return out

    regs, mem = _regs_mem_from_inp(inp)
    if not isinstance(regs, dict) or "rsp" not in regs:
        return {
            "ok": False,
            "pedagogy": _pedagogy_meta(student_mode=student_mode),
            "frame": {},
            "slots": [],
            "errors": ["Need input['regs'] with rsp (or initial_state.regs.rsp). For assembly + stack walks, also pass asm."],
        }

    rsp = regs.get("rsp")
    try:
        rsp_i = int(rsp) & MASK
    except Exception:
        return {
            "ok": False,
            "pedagogy": _pedagogy_meta(student_mode=student_mode),
            "frame": {},
            "slots": [],
            "errors": ["regs['rsp'] must be an integer."],
        }

    rbp_i = regs.get("rbp")
    try:
        rbp_val = int(rbp_i) & MASK if rbp_i is not None else None
    except Exception:
        rbp_val = None

    ws = int(inp.get("word_size", 8) or 8)
    if ws not in (1, 2, 4, 8):
        ws = 8
    max_slots = min(int(inp.get("max_slots", 32) or 32), 64)
    hints_in = inp.get("label_hints") or {}
    if not isinstance(hints_in, dict):
        hints_in = {}

    frame, slots, warnings = _build_slots(rsp_i, rbp_val, mem, word_size=ws, max_slots=max_slots, label_hints=hints_in)

    if student_mode:
        addrs_only = []
        for sl in slots[: max_slots]:
            addr = sl.get("addr")
            off = sl.get("offset_from_rbp")
            lab = sl.get("label")
            addrs_only.append(
                {
                    "addr": _hex(addr) if isinstance(addr, int) else addr,
                    "offset_from_rbp": off,
                    "label_guess": lab,
                    "value": None,
                    "note": "Predict the qword at this address from your trace before revealing.",
                }
            )
        return {
            "ok": True,
            "pedagogy": _pedagogy_meta(student_mode=True),
            "frame": frame,
            "slots": addrs_only,
            "table_md": _visualization_template_md(num_slots=min(8, len(addrs_only) or 6)),
            "warnings": warnings,
            "errors": [],
            "initialization_hints": [
                "Use the addresses and offsets to sketch stack growth toward lower vs higher addresses.",
                "After you write guessed values, call again with student_mode=false to compare to the modeled mem snapshot.",
            ],
        }

    return {
        "ok": True,
        "pedagogy": _pedagogy_meta(student_mode=False),
        "frame": frame,
        "slots": slots,
        "table_md": _stack_table_md(frame, slots),
        "warnings": warnings,
        "errors": [],
    }
