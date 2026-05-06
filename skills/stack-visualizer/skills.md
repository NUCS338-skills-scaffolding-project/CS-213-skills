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

# Stack Visualizer

## Description

Visualizes a slice of the stack around `rsp` (and optionally `rbp`) to help students understand stack frames and calling convention conventions. It formats addresses and qword values into a readable view and can add helpful labels (e.g., saved `rbp`, return address, locals) when enough context is provided.

## When to Trigger

- Student is confused about `rsp`/`rbp` and stack frame layout.
- Student wants to interpret a stack memory dump around `rsp`.

## Inputs

Describe what inputs the function expects.

## Outputs

Describe what the function returns.

## Usage

```python
from logic import run
print(run({"regs": {"rsp": 0x1000, "rbp": 0x1010}, "mem": {0x1010: 1, 0x1018: 2}}))
```
