---
skill_id: "stack-visualizer"
name: "Stack Visualizer"
skill_type: "code"
tags: ["stack", "cs213"]
course_types: ["cs"]
learning_goal_tags:
  - "trace-execution"
  - "specify-io"
trigger_signals:
  - "stack-layout-question"
  - "rsp-rbp-confusion"
chip_icon: "📚"
python_entry: "logic.py"
version: "0.1.0"
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
