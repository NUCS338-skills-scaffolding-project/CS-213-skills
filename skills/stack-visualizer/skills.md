---
skill_id: "stack-visualizer"
name: "Stack Visualizer"
skill_type: "code"
tags: ["stack", "rsp", "assembly", "cs213", "x86-64"]
course_types: ["cs"]
learning_goal_tags:
  - "trace-execution"
  - "specify-io"
trigger_signals:
  - "stack-layout-question"
  - "rsp-rbp-confusion"
  - "assembly-with-rsp-given"
  - "where-does-push-write"
  - "how-does-rsp-change"
chip_icon: "📚"
python_entry: "logic.py"
version: "0.2.0"
stance: "socratic"
---

# Stack Visualizer

## Description

Helps students reason about the **stack**: where **`rsp`** points, how it **moves** instruction-by-instruction, and what **qwords** in memory sit above it—especially for **Intel-syntax** snippets using `push` / `pop` / `mov` / `add` / `sub` (including **`add rsp, imm`** / **`sub rsp, imm`** frame adjustment). Two shapes:

1. **Snapshot** — no `asm`: given **`rsp`** (and optional **`rbp`**, **`mem`**, **`label_hints`**), builds an address/value table for a window of stack slots.
2. **Assembly timeline** — with **`asm`**: requires an explicit initial **`rsp`** (same register dict); simulates each line and returns per-step **`rsp_before` → `rsp_after`**, optional **`mem_write`** for `push`, a short note for `pop`, and a **stack window** (`slots` + `table_md`) after each instruction.

The tutor should **walk one instruction at a time**, ask the student to **predict** `rsp` and the relevant memory words, then confirm or nudge—**not** lead with the full numeric timeline as a finished answer.

## When to Trigger

- Student pastes **assembly** and gives an initial **stack pointer** (`rsp`, optionally `rbp` / memory model) and wants to see **how the stack is used** or how **`rsp` changes**.
- Student is confused about **`rsp` / `rbp`**, saved RBP, return address, locals, or **where `push` stores**.
- Student wants help **drawing or checking** stack memory contents (addresses + values) **after** they have tried a layout.

Do **not** prefer this skill when the student only wants a **non-stack execution trace** with no stack-pointer story—**execution-trace** may fit better.

## Pedagogy (must follow)

1. **No direct “here is the whole stack answer.”** Do not dump the entire `timeline` or every `table_md` as the first reply. Prefer **`student_mode: true`** in `run` so the tool returns **`timeline_hints`** (roles + questions) and a **blank ladder** template without numeric solutions.
2. **Anchor on their `rsp`.** If they have not fixed an initial `rsp` (and any modeled `mem` they care about), ask them to choose **concrete test values** and justify alignment (e.g. 8-byte slots for pushes).
3. **Line by line.** For each instruction, ask: Does **`rsp` change**? By how many bytes and in which direction? Is a **qword written or read** at the stack top? How does that relate to **offsets from `rbp`** when `rbp` is meaningful?
4. **Visualization.** Help them sketch ascending addresses vs stack growth; use **`table_md`** / slot lists **after** they predict, or use snapshot mode with **`student_mode: true`** to show **addresses and labels** with values elided (`value: null`) plus a markdown template they fill in.
5. **Verification.** After they commit to a trace, they (or you) may rerun with **`student_mode: false`** to compare numbers—frame it as checking their work, not replacing it.

## Inputs

| Key                                   | Meaning                                                                                           |
| ------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `asm`                                 | Optional. If non-empty, runs **timeline** mode (Intel-style subset in `logic.py`).                |
| `regs` / `mem`                        | Top-level register map and memory map **or** nested under `initial_state`.                        |
| `regs.rsp`                            | **Required** for timeline mode and for snapshot mode.                                             |
| `regs.rbp`                            | Optional; enables **offset-from-rbp** labeling when `rbp` lies above `rsp` in the modeled window. |
| `mem`                                 | Optional address → qword values for stack (and other) cells.                                      |
| `label_hints`                         | Optional `addr → label` overrides for the table.                                                  |
| `word_size`, `max_slots`, `max_steps` | Optional tuning (defaults 8, 16–32, 200).                                                         |
| `student_mode`                        | Optional `bool`. When `true`, omits numeric solution traces (see Outputs).                        |

## Outputs

- **Snapshot, `student_mode: false`:** `frame`, `slots`, `table_md`, `warnings`, **`pedagogy`**.
- **Snapshot, `student_mode: true`:** `slots` with addresses/labels but **`value` null** and a **`visualization_template_md`** ladder; **`initialization_hints`**.
- **Timeline, `student_mode: false`:** `timeline` (each step: `change` with `rsp_before` / `rsp_after` / `mem_write` / `mem_note`, `slots`, `table_md`), **`final_*`**, **`pedagogy`**.
- **Timeline, `student_mode: true`:** **`timeline_hints`** only (plus `visualization_template_md`, **`initialization_hints`**), **`pedagogy`** (`hints_only`); no per-step numeric `rsp` or memory answers in JSON.

## Usage

```python
from logic import run

# Snapshot around rsp
print(run({"regs": {"rsp": 0x1000, "rbp": 0x1010}, "mem": {0x1010: 1, 0x1018: 2}}))

# Assembly + rsp: full internal trace (use sparingly with students)
print(run({"asm": "push rbx\npop rax\n", "initial_state": {"regs": {"rsp": 0x1000, "rbx": 42}, "mem": {}}}))

# Hint scaffold for tutoring (preferred with students)
print(run({"asm": "push rbx\n", "initial_state": {"regs": {"rsp": 0x1000, "rbx": 1}}, "student_mode": True}))
```
