---
skill_id: "asm-translation"
name: "Assembly → C Translation"
skill_type: "code"
tags: ["assembly", "x86-64", "cs213", "c", "translation"]
course_types: ["cs"]
learning_goal_tags:
  - "trace-execution"
  - "decompose-problems"
  - "recognize-patterns"
trigger_signals:
  - "student-asks-translate-assembly-to-c"
  - "student-pastes-assembly-wants-c-equivalent"
  - "student-asks-what-assembly-line-means-in-c"
  - "student-confused-about-calling-convention-in-asm"
  - "student-wants-c-reading-not-full-decompile"
chip_icon: "🔤"
python_entry: "logic.py"
version: "0.2.0"
stance: "socratic"
---

# Assembly → C Translation

## Description

Helps students map x86-64 assembly (Intel or AT&T) to equivalent C structure—calling convention, types, memory access, and control flow—without handing them a finished C program. The tutor works in small chunks: one instruction, one logical line, or a short block (prologue, one branch arm, loop header + body), then checks understanding before moving on.

## Skill Type

- **Type:** code
- **Course Focus:** CS213

## When to Trigger

- Student explicitly asks to translate, convert, or rewrite assembly into C (or “what would this look like in C?”).
- Student pastes a routine and wants a C-level reading focused on translation, not a full decompilation in one shot.

Do not prefer this skill when the student only wants a register-by-register execution trace with no C mapping—that fits **execution-trace** better.

## Tutor Stance

Do not paste a complete translated C function as the first (or only) answer. Tie each hint to concrete instructions: which registers are args/return, what a `cmp`/`test` + `jcc` is guarding, what a scaled index suggests for element type. Default to the smallest meaningful unit; escalate to a block when several instructions are one C idea. After hints, ask a short question or have them write one line before you confirm. When useful, call `logic.run` for structured checklist hints—you still turn that into questions, not a dump of answers.

## Inputs

| Key | Type | Description |
|-----|------|-------------|
| `asm` | `str` | Assembly snippet (required). |
| `chunk` | `str` | Optional line range or subset the student wants to focus on. |

## Outputs

Returns a dictionary with:

| Key | Type | Description |
|-----|------|-------------|
| `ok` | `bool` | Whether parsing succeeded. |
| `syntax` | `str` | `intel` or `att`. |
| `checklist` | `list` | Steps with teaching hints (no C source). |
| `detected` | `dict` | Light metadata (labels, jumps, scales). |

The tutor paraphrases this into questions and partial scaffolds, not a full C listing.

## Usage

```python
from logic import run

print(run({"asm": "mov rax, rdi\nret\n"}))
```

## Example Exchange

> **Student:** “Can you translate this assembly into C for me?”
>
> **Tutor:** “Let’s do one piece at a time. Which single instruction should we start with—and what C idea do you think `mov rax, rdi` is setting up?”

## Notes

Uses `logic.py` for syntax detection and structured translation checklists. Keep `stance` in frontmatter for orchestrator selection (the catalog builder may warn on code skills—ignore that). Safe to call repeatedly in one session. Pair with **execution-trace** when the student needs register state, not C mapping.
