---
skill_id: "execution-trace"
name: "Execution Trace"
skill_type: "code"
tags: ["assembly", "trace", "cs213"]
course_types: ["cs"]
learning_goal_tags:
  - "trace-execution"
  - "identify-invariants"
trigger_signals:
  - "hand-trace-needed"
  - "register-state-question"
chip_icon: "📋"
python_entry: "logic.py"
version: "0.1.0"
---

# Execution Trace

## Description

Produces a step-by-step execution trace for small x86-64 snippets, showing register/memory state before and after each instruction. It’s designed for hand-tracing practice (not full emulation), focusing on a limited set of common Intel-syntax instructions.

## When to Trigger

- Student needs help hand-tracing a short assembly snippet.
- Student asks how a few instructions change registers/memory over time.

## Inputs

Describe what inputs the function expects.

## Outputs

Describe what the function returns.

## Usage

```python
from logic import run
print(run({"asm": "mov rax, 5\nadd rax, 3\n", "initial_state": {"regs": {"rsp": 0x1000}}}))
```
