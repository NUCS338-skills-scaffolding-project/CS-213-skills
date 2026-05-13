from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

import logic


def _read_text(path: str | None) -> str:
    if not path or path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _parse_json(s: str) -> Dict[str, Any]:
    s = (s or "").strip()
    if not s:
        return {}
    try:
        v = json.loads(s)
        return v if isinstance(v, dict) else {}
    except Exception:
        return {}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Trace assembly and show how the stack changes over time.")
    p.add_argument("--asm", help="Path to an asm file. Use '-' (or omit) to read from stdin.", default="-")
    p.add_argument("--syntax", choices=["auto", "intel", "att"], default="auto")
    p.add_argument("--initial", help="JSON dict for initial_state (e.g. '{\"regs\": {\"rsp\": 4096}, \"mem\": {}}')", default="")
    p.add_argument("--max-steps", type=int, default=200)
    p.add_argument("--max-slots", type=int, default=16)
    p.add_argument(
        "--student",
        action="store_true",
        help="Hint-only output (no numeric rsp/mem solution in timeline).",
    )
    args = p.parse_args(argv)

    asm = _read_text(args.asm)
    initial_state = _parse_json(args.initial)
    out = logic.run(
        {
            "asm": asm,
            "syntax": args.syntax,
            "initial_state": initial_state,
            "max_steps": args.max_steps,
            "max_slots": args.max_slots,
            "student_mode": args.student,
        }
    )

    if not out.get("ok"):
        for e in out.get("errors") or []:
            print("error:", e)
        return 2

    if args.student:
        hints = out.get("timeline_hints") or []
        for h in hints:
            step = h.get("step")
            asm_line = (h.get("asm") or "").rstrip("\n")
            print(f"\n--- step {step} (hints): {asm_line}")
            for r in h.get("stack_roles") or []:
                print(" ", r)
            for q in h.get("questions") or []:
                print(" Q:", q)
        if out.get("visualization_template_md"):
            print("\n" + str(out["visualization_template_md"]))
        return 0

    timeline = out.get("timeline") or []
    for t in timeline:
        step = t.get("step")
        asm_line = (t.get("asm") or "").rstrip("\n")
        ch = t.get("change") or {}
        rsp_b = ch.get("rsp_before")
        rsp_a = ch.get("rsp_after")
        mw = ch.get("mem_write")
        mem_note = ch.get("mem_note")
        print(f"\n--- step {step}: {asm_line}")
        print(f"rsp: {hex(rsp_b) if isinstance(rsp_b, int) else rsp_b} -> {hex(rsp_a) if isinstance(rsp_a, int) else rsp_a}")
        if isinstance(mw, dict) and mw.get("kind") == "mem":
            addr = mw.get("addr")
            val = mw.get("value")
            addr_s = hex(addr) if isinstance(addr, int) else addr
            val_s = hex(val) if isinstance(val, int) else val
            print(f"mem_write: [{addr_s}] = {val_s}")
        if mem_note:
            print("note:", mem_note)

        slots = t.get("slots") or []
        for s in slots[: min(len(slots), 10)]:
            addr = s.get("addr")
            off = s.get("offset_from_rbp")
            val = s.get("value")
            label = s.get("label")
            addr_s = hex(addr) if isinstance(addr, int) else addr
            val_s = hex(val) if isinstance(val, int) else val
            print({"addr": addr_s, "off_rbp": off, "value": val_s, "label": label})

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

