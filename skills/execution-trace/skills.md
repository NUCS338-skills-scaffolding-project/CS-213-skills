---
skill_id: "execution-trace"
name: "Execution Trace"
skill_type: "code"
tags: ["assembly", "trace", "cs213", "x86-64", "registers"]
course_types: ["cs"]
learning_goal_tags:
  - "trace-execution"
  - "identify-invariants"
trigger_signals:
  - "student-wants-hand-trace-assembly-homework"
  - "student-asks-register-values-after-instruction"
  - "student-stepping-through-assembly-line-by-line"
  - "student-asks-what-rdi-rax-contain-after-line"
  - "student-needs-initial-register-values-for-trace"
chip_icon: "📋"
python_entry: "logic.py"
version: "0.2.0"
stance: "socratic"
---

# Execution Trace

## Description

Supports hand-tracing small x86-64 snippets (Intel-style `mov` / `add` / `sub` / `push` / `pop` and `qword ptr [...]` per `logic.py`). The focus is register and memory state over time, plus choosing sensible initial inputs (argument registers, `rsp`, stack/memory slots) so the snippet behaves as intended. The tutor goes one instruction at a time, checks the student’s predicted state, then moves on.

This skill is for execution and state, not mapping assembly to C—that is **asm-translation**.

## Skill Type

- **Type:** code
- **Course Focus:** CS213

## When to Trigger

- Student wants to step through assembly and understand what lives in which register after each line.
- Student asks how inputs (`rdi`, `rsi`, `rdx`, stack, memory) should be set so the code does the right thing.
- Student asks for a hand trace or register values over a short listing.

## Tutor Stance

Do not dump the full sequence of final register values or paste the complete `after` / `delta` column for every line as your first move. Pick one instruction; ask what it reads, what it writes, and what the student predicts before vs after. If the snippet uses argument registers or stack slots, ask what concrete values they want to assume and why. Optionally call `logic.run` with `student_mode: true` so JSON gives scaffolding without revealing simulated `after` states. Only after they trace a line may you confirm their numbers—frame it as checking their work.

## Inputs

| Key | Type | Description |
|-----|------|-------------|
| `asm` | `str` | Assembly snippet (required), Intel-style subset in `logic.py`. |
| `initial_state` | `dict` | Optional `{"regs": {...}, "mem": {...}}`; 64-bit values. |
| `student_mode` | `bool` | When `true`, omits per-step `after` / `delta` / full solution table. |

## Outputs

| Mode | Keys | Use |
|------|------|-----|
| `student_mode: false` | `steps`, `walkthrough_table_md`, `final_state` | Answer keys or internal checks—not wholesale student replies. |
| `student_mode: true` | hint scaffolds, `pedagogy.hints_only` | Student-facing tutoring. |

## Usage

```python
from logic import run

# Student-facing scaffolding (no revealed after-states)
print(run({"asm": "mov rax, 5\nadd rax, 3\n", "student_mode": True}))

# Full internal trace (verify after student predicts)
print(run({"asm": "mov rax, 5\nadd rax, 3\n", "initial_state": {"regs": {"rsp": 0x1000}}}))
```

## Example Exchange

> **Student:** “What are the registers after these three instructions?”
>
> **Tutor:** “Let’s take them one at a time. For the first `mov`, which operand is the destination and what value do you predict in `rax` before we look at the next line?”

## Notes

Always prefer `student_mode: true` with students. Full traces are for post-prediction checks only. Keep `stance` in frontmatter for orchestrator selection (catalog may warn on code skills—ignore). Pair with **asm-translation** when the student wants C mapping, not register state.
