from __future__ import annotations

import logic


def _print_case(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def _run(asm: str, syntax: str = "auto") -> None:
    out = logic.run({"asm": asm, "syntax": syntax})
    print("ok:", out.get("ok"), "syntax:", out.get("syntax"))
    if out.get("errors"):
        print("errors:", out["errors"])
    if out.get("warnings"):
        print("warnings:", out["warnings"][:3])
    pseudo = out.get("pseudocode") or ""
    if pseudo.strip():
        print("\nPSEUDOCODE:\n" + pseudo)
    lm = out.get("line_map") or []
    explained = [x for x in lm if x.get("kind") == "instruction"]
    if explained:
        print("example_explanation:", explained[0].get("explanation"))


def main() -> None:
    _print_case("Case 1: Intel syntax basics (mov/lea/add)")
    _run(
        """
push rbp
mov rbp, rsp
sub rsp, 16
mov DWORD PTR [rbp-4], edi
lea eax, [edi+edi*2]
add eax, 7
""".strip(),
        syntax="intel",
    )

    _print_case("Case 2: AT&T syntax memory addressing")
    _run(
        """
pushq %rbp
movq %rsp, %rbp
subq $16, %rsp
movl %edi, -4(%rbp)
leal (%rdi,%rdi,2), %eax
addl $7, %eax
""".strip(),
        syntax="att",
    )

    _print_case("Case 3: Branch/compare (warns about flags/CFG)")
    _run(
        """
cmpl $0, %edi
jle .Ldone
addl $1, %edi
.Ldone:
ret
""".strip(),
        syntax="att",
    )

    _print_case("Case 4: Empty asm (error path)")
    out = logic.run({"asm": ""})
    print("ok:", out.get("ok"))
    print("errors:", out.get("errors"))


if __name__ == "__main__":
    main()

