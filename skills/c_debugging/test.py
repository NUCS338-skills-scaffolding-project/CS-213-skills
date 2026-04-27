from __future__ import annotations

import logic


def _print_case(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def _run_case(payload: dict) -> None:
    out = logic.run(payload)
    print("ok:", out.get("ok"))

    msg = out.get("message")
    if isinstance(msg, str) and msg.strip():
        print("\n" + msg.rstrip() + "\n")

    likely = out.get("likely_root_causes") or []
    if likely:
        top = likely[0]
        print("top_cause:", top.get("title"), "(confidence:", top.get("confidence"), ")")
        ev = top.get("evidence") or []
        if ev:
            print("evidence:", ev[0])

    steps = out.get("next_steps") or []
    if steps:
        print("next_step:", steps[0])

    errs = out.get("errors") or []
    if errs:
        print("errors:", errs)


def main() -> None:
    _print_case("Case 1: NULL dereference segfault")
    _run_case(
        {
            "c_code": "int *p = NULL; *p = 3;",
            "symptoms": "segmentation fault",
            "constraints": {"tools_allowed": ["gdb", "asan"]},
        }
    )

    _print_case("Case 2: printf format mismatch warning")
    _run_case(
        {
            "c_code": 'long x = 5; printf("%d\\n", x);',
            "compiler_output": "warning: format specifies type 'int' but the argument has type 'long'",
            "constraints": {"tools_allowed": ["valgrind"]},
        }
    )

    _print_case("Case 3: stack smashing / buffer overflow hint")
    _run_case(
        {
            "c_code": "char buf[8]; strcpy(buf, input);",
            "runtime_output": "*** stack smashing detected ***: terminated",
            "constraints": {"tools_allowed": ["asan", "gdb"]},
        }
    )

    _print_case("Case 4: malloc without free (leak heuristic)")
    _run_case(
        {
            "c_code": "int *a = malloc(10 * sizeof(int)); a[0] = 1; return 0;",
            "symptoms": "works but memory usage grows over time",
            "constraints": {"tools_allowed": ["valgrind"]},
        }
    )

    _print_case("Case 5: empty input (error path)")
    _run_case({})


if __name__ == "__main__":
    main()

