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

# Assembly Translation

## Description

Guides students from x86-64 assembly toward C-level meaning using a TA-style checklist (calling convention, data sizes, addressing modes, and control-flow structure). It provides structured hints and intermediate observations rather than attempting to fully decompile code.

## When to Trigger

- Student pastes assembly and asks what it “does” at a high level.
- Student needs help mapping instructions to variables, types, and control flow.

## Inputs

Describe what inputs the function expects.

## Outputs

Describe what the function returns.

## Usage

```python
from logic import run
print(run({"asm": "mov rax, rdi\nret\n"}))
```
