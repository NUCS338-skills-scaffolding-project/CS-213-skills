---
skill_id: "execution_trace"
name: "Execution Trace (simple)"
skill_type: "code"
tags: ["assembly", "trace", "cs213"]
python_entry: "logic.py"
---

# Execution Trace (simple)

## Description

Steps **Intel-style** `mov`, `add`, `sub`, `push`, `pop` on 64-bit registers and `qword ptr [reg±disp]` memory.

## When to Trigger

- Small hand-trace homework snippets.

## Inputs

- `asm` (str, required)
- `initial_state` (optional): `{"regs": {...}, "mem": {...}}`

## Outputs

- `ok`, `steps` (each with `before` / `after` / optional `error`, plus `delta` + `delta_summary`), `final_state`, `errors`.

## Usage

```python
from logic import run
print(run({"asm": "mov rax, 5\nadd rax, 3\n", "initial_state": {"regs": {"rsp": 0x1000}}}))
```

## Notes

Unsupported instructions stop the trace with `ok: false`.
