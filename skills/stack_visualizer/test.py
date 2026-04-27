from __future__ import annotations

import logic


def _print_case(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def _run(payload: dict) -> None:
    out = logic.run(payload)
    print("ok:", out.get("ok"))
    if out.get("warnings"):
        print("warnings:", out["warnings"])
    if out.get("errors"):
        print("errors:", out["errors"])
    frame = out.get("frame") or {}
    if frame:
        print("frame:", frame)
    slots = out.get("slots") or []
    # Print a small, readable subset
    for s in slots[:10]:
        addr = s.get("addr")
        val = s.get("value")
        label = s.get("label")
        off = s.get("offset_from_rbp")
        addr_s = hex(addr) if isinstance(addr, int) else addr
        val_s = hex(val) if isinstance(val, int) else val
        off_s = off if off is None else int(off)
        print({"addr": addr_s, "off_rbp": off_s, "value": val_s, "label": label})


def main() -> None:
    _print_case("Case 1: Typical frame (saved rbp + return address present)")
    _run(
        {
            "regs": {"rsp": 0x1000, "rbp": 0x1010},
            "mem": {
                0x1000: 0x0,
                0x1008: 0x1111,
                0x1010: 0x2020,  # saved rbp
                0x1018: 0x400123,  # return address
            },
            "max_slots": 8,
        }
    )

    _print_case("Case 2: rbp missing (fallback window)")
    _run({"regs": {"rsp": 0x2000}, "mem": {0x2000: 0xAAAA, 0x2008: 0xBBBB}, "max_slots": 4})

    _print_case("Case 3: label_hints override")
    _run(
        {
            "regs": {"rsp": 0x3000, "rbp": 0x3010},
            "mem": {0x3018: 0xDEADBEEF},
            "label_hints": {0x3018: "return_address (hinted)"},
            "max_slots": 6,
        }
    )

    _print_case("Case 4: bad input (error path)")
    _run({"regs": {}})


if __name__ == "__main__":
    main()

