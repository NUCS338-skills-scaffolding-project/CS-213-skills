---
skill_id: "c-debugger"
name: "C Debugger"
skill_type: "code"
tags: ["c", "debugging", "cs213"]
course_types: ["cs"]
learning_goal_tags:
  - "debug-systematically"
trigger_signals:
  - "c-code-bug-question"
  - "whats-wrong-with-my-c"
  - "compile-error"
  - "segfault"
  - "runtime-error"
chip_icon: "🐛"
python_entry: "logic.py"
version: "0.2.0"
stance: "socratic"
---

# C Debugger

## Description

Supports **systematic C debugging** when the student has shared **C source** and is asking about **bugs, crashes, or wrong behavior**. The tutor turns symptoms and code into **investigation hints**: categories to consider, questions to ask themselves, and **process** next steps (warnings, sanitizers, narrowing the failure)—not a ready-made patch.

## When to Trigger

- Student pastes **C code** and asks what is wrong, why it crashes, why the output is incorrect, or similar **bug-focused** questions.
- Student shares **compiler or runtime output** (or a short symptom description) together with code and wants help **debugging**.

Prefer a lighter skill if they only want generic study tips without code or errors.

## Pedagogy (must follow)

1. **No direct fix.** Do not spell out the exact code change (e.g. “change `i <= n` to `i < n`” or “add `free` here”) unless the student has already identified the issue and you are confirming or they explicitly ask for a minimal correction after working through it.
2. **No “the bug is on line X.”** Do not single out a line or variable as **the** answer. You may teach **how** to use tools that _they_ use to locate a line (gdb, sanitizer output, bisecting), or ask which line _they_ suspect and why.
3. **Hints and questions.** Prefer: “What must be true right before this dereference?” “What does the compiler warning point at—prototype, type, or lifetime?” “If you print or gdb-inspect these two values at this point, what would falsify your guess?”
4. **One layer at a time.** Offer a small next step; after they respond, narrow or deepen. Optional: call `logic.run` and **turn its structured items into Socratic prompts**, not a dump of “root cause” as fact.
5. **Sanitizers and gdb** as _skills to practice_, not as commands that magically reveal the answer without their interpretation.

## Inputs

| Key                         | Meaning                                                                                     |
| --------------------------- | ------------------------------------------------------------------------------------------- |
| `c_code`                    | C source (recommended when debugging).                                                      |
| `compiler_output`           | Full compiler stderr (warnings help).                                                       |
| `runtime_output`            | Crash message, sanitizer snippet, or wrong output.                                          |
| `symptoms`                  | Short free-text if logs are incomplete.                                                     |
| `constraints.tools_allowed` | Optional list, e.g. `["gdb","asan","valgrind","ubsan"]`, to tailor **process** suggestions. |

## Outputs

`run` returns JSON: `likely_root_causes` (each item is an **investigation angle** with `what_to_check` prompts, not a verdict), `questions_to_ask`, `next_steps`, optional `warnings` / `errors`, a human-readable `message`, and **`pedagogy`** metadata (`hints_only`). The agent must still **rephrase** toward questions, not line-level fixes.

## Usage

```python
from logic import run
print(run({"c_code": "int *p=NULL; *p=1;", "symptoms": "segfault"}))
```
