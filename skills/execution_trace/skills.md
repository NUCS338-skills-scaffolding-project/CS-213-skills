---
skill_id: "execution_trace"
name: "Execution Trace (Registers/Memory)"
skill_type: "code"
tags: ["assembly", "x86-64", "tracing", "registers", "memory", "cs213"]
python_entry: "logic.py"
---

# Execution Trace (Registers/Memory)

## Description

Simulates (a subset of) x86-64 instruction execution step-by-step, producing a trace of register/memory changes. Useful for helping students build correct hand-traces and for validating a student’s proposed state transitions.

## When to Trigger

- Student is asked to “trace this code” and is unsure how registers/stack change
- Student needs to understand effects of `push/pop/mov/lea/add/sub/call/ret` on `%rsp/%rbp`
- Student provides an execution trace and asks “is this correct?”

## Inputs

`run(input: dict) -> dict`

Required keys:
- `asm` (str): assembly snippet to trace (single basic-block style works best)

Optional keys:
- `syntax` (str): `"att" | "intel" | "auto"` (default `"auto"`)
- `initial_state` (dict):
  - `regs` (dict[str,int]): e.g. `{"rsp": 0x7fffffffe000, "rbp": 0x0, "rax": 1}`
  - `mem` (dict[int,int]): memory as qword map: address -> 0..2^64-1 (default `{}`)
- `max_steps` (int): maximum instructions to execute (default `200`)
- `stop_on_error` (bool): stop tracing when an instruction can’t be executed (default `True`)

## Outputs

A dict:
- `ok` (bool)
- `syntax` (str)
- `steps` (list[dict]): one entry per executed instruction:
  - `ip` (int): step index (0-based)
  - `asm` (str): raw line
  - `instruction` (dict): parsed instruction
  - `before` / `after` (dict): snapshots of regs (and touched mem)
  - `diff` (dict): compact changes (regs + mem writes)
- `final_state` (dict)
- `warnings` (list[str])
- `errors` (list[str])

## Usage

```python
from logic import run

asm = """
push rbp
mov rbp, rsp
sub rsp, 16
mov QWORD PTR [rbp-8], rdi
mov rax, QWORD PTR [rbp-8]
add rax, 3
"""

out = run({
  "asm": asm,
  "syntax": "intel",
  "initial_state": {"regs": {"rsp": 0x1000, "rbp": 0x0, "rdi": 5}, "mem": {}},
})
print(out["steps"][-1]["after"]["regs"]["rax"])
```

## Notes

- **Memory model**: default is a qword-addressed map (address -> 64-bit value). This is intentionally simplified for intro tracing.
- **Edge cases**: partial registers (`eax`, `al`), flags, and complex control flow are not fully modeled; the tracer will warn or error when it can’t safely proceed.
