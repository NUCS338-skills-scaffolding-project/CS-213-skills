---
skill_id: "c_debugging"
name: "C Debugging Triage"
skill_type: "code"
tags: ["c", "debugging", "segfault", "undefined-behavior", "memory", "cs213"]
python_entry: "logic.py"
---

# C Debugging Triage

## Description

Analyzes a C snippet plus symptoms (compiler errors, runtime messages, or observed behavior) and returns likely root causes with concrete next debugging steps. Tailored for intro systems patterns like segfaults, pointer mistakes, memory leaks, and UB.

## When to Trigger

- Student reports segfault / bus error / “it crashes”
- Student shares C code + confusing compiler warnings/errors
- Student sees wrong output and suspects pointer/array arithmetic bugs

## Inputs

`run(input: dict) -> dict`

Optional keys (best results with more context):
- `c_code` (str): C code or excerpt
- `compiler_output` (str): gcc/clang warnings/errors
- `runtime_output` (str): program output / crash message
- `symptoms` (list[str] | str): brief description (“segfault at line…”, “valgrind invalid read…”)
- `constraints` (dict): e.g. `{"tools_allowed": ["gdb", "valgrind", "asan"]}`

## Outputs

A dict:
- `ok` (bool)
- `likely_root_causes` (list[dict]): ranked hypotheses:
  - `title` (str), `confidence` (0..1), `evidence` (list[str]), `what_to_check` (list[str])
- `questions_to_ask` (list[str])
- `next_steps` (list[str]): actionable commands or edits to try
- `warnings` (list[str])
- `errors` (list[str])

## Usage

```python
from logic import run

out = run({
  "c_code": "int *p = NULL; *p = 3;",
  "symptoms": "segmentation fault",
  "constraints": {"tools_allowed": ["gdb", "asan"]},
})
print(out["likely_root_causes"][0]["title"])
print(out["next_steps"][:3])
```

## Notes

- This is a **triage assistant**, not a full static analyzer. It uses pattern matching and common CS-213 failure modes to generate hypotheses.
- Edge cases: multi-file builds, optimizer effects, concurrency bugs.
