---
skill_id: "c-debugger"
name: "C Debugger"
skill_type: "code"
tags: ["c", "debugging", "cs213"]
course_types: ["cs"]
learning_goal_tags:
  - "debug-systematically"
trigger_signals:
  - "compile-error"
  - "segfault"
  - "runtime-error"
chip_icon: "🐛"
python_entry: "logic.py"
version: "0.1.0"
---

# C Debugger

## Description

Helps students debug C issues (compile errors, runtime errors, segfaults) by turning symptoms and output into a short, systematic triage plan. It provides likely root causes plus targeted questions and next steps rather than claiming a single definitive “bug line.”

## When to Trigger

- Student shares C code and compiler/runtime output and asks “what’s wrong?”
- Student reports a segfault or mysterious runtime behavior and needs a debugging plan.

## Inputs

Describe what inputs the function expects.

## Outputs

Describe what the function returns.

## Usage

```python
from logic import run
print(run({"c_code": "int *p=NULL; *p=1;", "symptoms": "segfault"}))
```
