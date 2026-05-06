---
skill_id: "asm-translation"
name: "Assembly Translation"
skill_type: "code"
tags: ["assembly", "x86-64", "cs213"]
course_types: ["cs"]
learning_goal_tags:
  - "trace-execution"
  - "decompose-problems"
trigger_signals:
  - "student-reading-assembly"
  - "asm-to-c-question"
chip_icon: "🔤"
python_entry: "logic.py"
version: "0.1.0"
---

# Assembly Translation (TA-style)

## Description

TA-style checklist hints to relate **Intel-style x86-64** assembly to **C-level meaning**: infer signature/types from calling convention + addressing scales, identify control-flow skeleton (if/loops/switch), then focus on the logical “kernel”. Teaching helper, not a full decompiler.

## When to Trigger

- Student pastes assembly and wants a quick read on what instructions “mean”.

## Inputs

- `asm` (str, required): assembly source.

## Outputs

- `ok`, `syntax` (`att` or `intel` guess), `checklist` (ordered steps with hints), `detected` (small diagnostics), `errors`.

## Usage

```python
from logic import run
print(run({"asm": "mov rax, rdi\nret\n"}))
```

## Notes

Not a full disassembler—teaching helper only.
