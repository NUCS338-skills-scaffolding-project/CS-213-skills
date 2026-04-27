from __future__ import annotations

import logic


def _print_case(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def _run(payload: dict) -> None:
    out = logic.run(payload)
    print("ok:", out.get("ok"), "syntax:", out.get("syntax"))
    if out.get("warnings"):
        print("warnings:", out["warnings"][:3])
    if out.get("errors"):
        print("errors:", out["errors"][:3])
    steps = out.get("steps") or []
    print("steps:", len(steps))
    if steps:
        last = steps[-1]
        print("last_diff_regs:", (last.get("diff") or {}).get("regs"))
    fs = out.get("final_state") or {}
    regs = (fs.get("regs") or {})
    # Print a few common regs if present
    for r in ("rax", "rdi", "rsp", "rbp", "rip"):
        if r in regs:
            print(f"{r} =", hex(regs[r]) if isinstance(regs[r], int) else regs[r])


def main() -> None:
    _print_case("Case 1: Intel prologue + simple arithmetic")
    asm = """
push rbp
mov rbp, rsp
sub rsp, 16
mov rax, 5
add rax, 3
""".strip()
    _run({"asm": asm, "syntax": "intel", "initial_state": {"regs": {"rsp": 0x1000, "rbp": 0x0}}})

    _print_case("Case 2: Memory store/load via [rbp-8]")
    asm = """
push rbp
mov rbp, rsp
sub rsp, 16
mov QWORD PTR [rbp-8], rdi
mov rax, QWORD PTR [rbp-8]
""".strip()
    _run({"asm": asm, "syntax": "intel", "initial_state": {"regs": {"rsp": 0x2000, "rbp": 0x0, "rdi": 0x1234}, "mem": {}}})

    _print_case("Case 3: Unsupported instruction (error path)")
    asm = "nop"
    _run({"asm": asm, "syntax": "intel", "initial_state": {"regs": {"rsp": 0x3000}}})

    _print_case("Case 4: Branch instruction (warning path, continues)")
    asm = """
cmp rdi, 0
jne somewhere
add rdi, 1
""".strip()
    _run({"asm": asm, "syntax": "intel", "initial_state": {"regs": {"rsp": 0x4000, "rdi": 0}}})


if __name__ == "__main__":
    main()

