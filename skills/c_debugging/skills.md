---
skill_id: "c_debugging"
name: "C Debugging Triage"
skill_type: "code"
tags: ["c", "debugging", "cs213"]
python_entry: "logic.py"
---

# C Debugging Triage

## Description

Pattern-matches common C/systems bugs (segfaults, format strings, heap issues) and returns ranked guesses plus a readable `message`. The guidance is **hint-driven** (TA-style): it avoids pinpointing an exact line/function as “the bug” and instead suggests what to inspect and how to narrow it down.

## When to Trigger

- Student shares C code and/or compiler or runtime output.

## Inputs (all optional, need at least one)

- `c_code`, `compiler_output`, `runtime_output`, `symptoms`
- `constraints.tools_allowed`: e.g. `["gdb", "asan", "valgrind"]`

## Outputs

- `ok`, `likely_root_causes`, `questions_to_ask`, `next_steps`, `message`, `errors`

## Usage

```python
from logic import run
print(run({"c_code": "int *p=NULL; *p=1;", "symptoms": "segfault"}))
```
