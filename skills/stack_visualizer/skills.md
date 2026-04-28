---
skill_id: "stack_visualizer"
name: "Stack Visualizer (simple)"
skill_type: "code"
tags: ["stack", "cs213"]
python_entry: "logic.py"
---

# Stack Visualizer (simple)

## Description

Shows qword stack slots from `rsp` through a small window, with optional `rbp`-relative labels (`saved_rbp`, `return_address`, `local[...]`).

## When to Trigger

- Explain stack layout from known `rsp`/`rbp` and memory.

## Inputs

- `regs` (dict): at least `rsp`; optional `rbp`
- `mem` (dict, optional): address → qword value
- `word_size`, `max_slots`, `label_hints` (optional)

## Outputs

- `ok`, `frame`, `slots`, `table_md` (markdown table), `warnings`, `errors`

## Usage

```python
from logic import run
print(run({"regs": {"rsp": 0x1000, "rbp": 0x1010}, "mem": {0x1010: 1, 0x1018: 2}}))
```
