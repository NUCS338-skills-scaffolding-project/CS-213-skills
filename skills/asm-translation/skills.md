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
  - "translate-assembly-to-c"
  - "translate-this-assembly"
  - "asm-to-c-translation"
  - "what-is-this-asm-in-c"
chip_icon: "🔤"
python_entry: "logic.py"
version: "0.2.0"
stance: "socratic"
---

# Assembly → C Translation

## Description

Helps students map **x86-64 assembly (Intel or AT&T)** to **equivalent C structure**—calling convention, types, memory access, and control flow—without handing them a finished C program. The tutor works in **small chunks**: one instruction, one logical line, or a short block (e.g. prologue, one branch arm, loop header + body) that hangs together, then checks understanding before moving on.

## When to Trigger

- Student explicitly asks to **translate**, **convert**, or **rewrite** assembly into C (or “what would this look like in C?”).
- Student pastes a routine and wants a **C-level reading** focused on translation, not a full decompilation in one shot.

Do **not** prefer this skill when the student only wants a **register-by-register execution trace** with no C mapping—that fits **execution-trace** better.

## Pedagogy (must follow)

1. **No direct full solution.** Do not paste a complete translated C function as the first (or only) answer. It is fine to show **fragments** with placeholders (e.g. `if (/* what compares to what? */) { ... }`) after the student has reasoned partway.
2. **Hint from what the assembly does.** Tie each hint to concrete instructions: which registers are args/return, what a `cmp`/`test` + `jcc` is guarding, what a scaled index suggests for element type, etc.
3. **Line-by-line or by logical block.** Default to the **smallest meaningful unit**; escalate to a block when several instructions are one C idea (e.g. `lea` + `mov` setting up an address). Ask: “Which single instruction should we do next?” or “Should we treat these four lines as one `if`?”
4. **Socratic checks.** After hints, ask a short question (“What C type fits a scale of 4 here?”) or have them write one line before you confirm or nudge.
5. **Optional tool use.** When useful, call `logic.py`’s `run` for structured checklist hints (calling convention, scales, branches)—still **you** turn that into questions, not a dump of answers.

## Inputs

| Key                                                                                                                           | Meaning                                  |
| ----------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| `asm`                                                                                                                         | String: the assembly snippet (required). |
| Optional: student’s **current chunk** (line range or pasted subset) if they want to focus translation on part of the routine. |

## Outputs

`run` returns JSON: `ok`, `syntax` (`intel` \| `att`), a **`checklist`** of steps with teaching hints (no C source), plus light **`detected`** metadata (labels, jumps, scales). The tutor **paraphrases** this into questions and partial scaffolds, not a full C listing.

## Usage

```python
from logic import run
print(run({"asm": "mov rax, rdi\nret\n"}))
```
