---
skill_id: "c-debugger"
name: "C Debugger"
skill_type: "code"
tags: ["c", "debugging", "cs213"]
course_types: ["cs"]
learning_goal_tags:
  - "debug-systematically"
trigger_signals:
  - "student-pastes-c-code-asks-what-is-wrong"
  - "student-reports-segfault-with-code-snippet"
  - "student-pastes-compiler-warning-with-code"
  - "student-says-output-is-wrong-not-crashing"
  - "student-asks-how-to-debug-with-gdb-or-sanitizer"
chip_icon: "🐛"
python_entry: "logic.py"
version: "0.2.0"
stance: "socratic"
---

# C Debugger

## Description

Supports systematic C debugging when the student has shared C source and is asking about bugs, crashes, or wrong behavior. The tutor turns symptoms and code into investigation hints: categories to consider, questions to ask themselves, and process next steps (warnings, sanitizers, narrowing the failure)—not a ready-made patch.

## Skill Type

- **Type:** code
- **Course Focus:** CS213

## When to Trigger

- Student pastes C code and asks what is wrong, why it crashes, or why the output is incorrect.
- Student shares compiler or runtime output (or a short symptom description) together with code and wants help debugging.

Prefer a lighter skill if they only want generic study tips without code or errors.

## Tutor Stance

Do not spell out the exact code change unless the student has already identified the issue and you are confirming. Do not single out a line or variable as the answer—you may teach how to use gdb or sanitizer output, or ask which line they suspect and why. Prefer process questions: “What must be true right before this dereference?” Offer one small next step at a time. Optional: call `logic.run` and turn structured items into Socratic prompts, not a dump of “root cause” as fact.

## Inputs

| Key | Type | Description |
|-----|------|-------------|
| `c_code` | `str` | C source (recommended when debugging). |
| `compiler_output` | `str` | Full compiler stderr (warnings help). |
| `runtime_output` | `str` | Crash message, sanitizer snippet, or wrong output. |
| `symptoms` | `str` | Short free-text if logs are incomplete. |
| `constraints.tools_allowed` | `list` | Optional, e.g. `["gdb","asan","valgrind","ubsan"]`. |

## Outputs

Returns a dictionary with:

| Key | Type | Description |
|-----|------|-------------|
| `likely_root_causes` | `list` | Investigation angles with `what_to_check` prompts, not verdicts. |
| `questions_to_ask` | `list` | Socratic prompts for the student. |
| `next_steps` | `list` | Process suggestions (tools, narrowing). |
| `message` | `str` | Human-readable summary. |
| `pedagogy` | `dict` | Metadata (`hints_only`). |

## Usage

```python
from logic import run

print(run({"c_code": "int *p=NULL; *p=1;", "symptoms": "segfault"}))
```

## Example Exchange

> **Student:** “My program segfaults on this line but I don’t know why.”
>
> **Tutor:** “Before we blame that line—what must be true about the pointer right before the dereference? What would you check in gdb or with a print to falsify your guess?”

## Notes

Uses `logic.py` to classify symptoms into investigation angles. Keep `stance` in frontmatter for orchestrator selection (catalog may warn on code skills—ignore). The tutor must rephrase JSON into process questions—never line-level fixes. Safe to call repeatedly as the student narrows the failure.
