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
  - "student-confused-about-rsp-and-rbp"
  - "student-asks-where-push-writes-on-stack"
  - "student-given-rsp-wants-stack-layout"
  - "student-asks-how-rsp-changes-each-instruction"
  - "student-drawing-stack-frame-for-assembly"
chip_icon: "📚"
python_entry: "logic.py"
version: "0.2.0"
stance: "socratic"
---

# Stack Visualizer

## Description

Helps students reason about the stack: where `rsp` points, how it moves instruction-by-instruction, and what qwords in memory sit above it—especially for Intel-syntax snippets using `push` / `pop` / `mov` / `add` / `sub` (including `add rsp, imm` / `sub rsp, imm` frame adjustment). Supports snapshot mode (given `rsp` and memory) or assembly timeline mode (per-step `rsp` and stack windows).

The tutor walks one instruction at a time, asks the student to predict `rsp` and relevant memory words, then confirms or nudges—not a full numeric timeline as the first reply.

## Skill Type

- **Type:** code
- **Course Focus:** CS213

## When to Trigger

- Student pastes assembly with an initial stack pointer and wants to see how the stack is used or how `rsp` changes.
- Student is confused about `rsp` / `rbp`, saved RBP, return address, locals, or where `push` stores.
- Student wants help drawing or checking stack memory after they have tried a layout.

Do not prefer this skill when the student only wants a non-stack execution trace—**execution-trace** may fit better.

## Tutor Stance

Do not dump the entire `timeline` or every `table_md` as the first reply. Prefer `student_mode: true` so the tool returns `timeline_hints` and blank ladder templates. If they have not fixed an initial `rsp`, ask them to choose concrete test values and justify alignment. For each instruction, ask whether `rsp` changes, by how many bytes, and whether a qword is written or read at the stack top. After they commit, rerun with `student_mode: false` only to verify—not to replace their trace.

## Inputs

| Key | Type | Description |
|-----|------|-------------|
| `asm` | `str` | Optional; non-empty runs timeline mode. |
| `regs` / `mem` | `dict` | Top-level or under `initial_state`; `regs.rsp` required. |
| `regs.rbp` | `int` | Optional; enables offset-from-rbp labeling. |
| `label_hints` | `dict` | Optional `addr → label` overrides. |
| `student_mode` | `bool` | When `true`, omits numeric solution traces. |
| `word_size`, `max_slots`, `max_steps` | `int` | Optional tuning. |

## Outputs

| Mode | Contents |
|------|----------|
| Snapshot, `student_mode: false` | `frame`, `slots`, `table_md`, `warnings` |
| Snapshot, `student_mode: true` | addresses/labels with `value: null`, `visualization_template_md` |
| Timeline, `student_mode: false` | `timeline` with `rsp_before` / `rsp_after`, per-step `table_md` |
| Timeline, `student_mode: true` | `timeline_hints`, `visualization_template_md` only |

## Usage

```python
from logic import run

# Snapshot around rsp
print(run({"regs": {"rsp": 0x1000, "rbp": 0x1010}, "mem": {0x1010: 1}}))

# Hint scaffold (preferred with students)
print(run({
    "asm": "push rbx\n",
    "initial_state": {"regs": {"rsp": 0x1000, "rbx": 1}},
    "student_mode": True,
}))
```

## Example Exchange

> **Student:** “Where does `push %rbx` write on the stack?”
>
> **Tutor:** “Before we read memory—by how many bytes should `rsp` move on a 64-bit push, and in which direction? After you predict the new `rsp`, where is the qword written relative to it?”

## Notes

`regs.rsp` is required. Full `timeline` / `table_md` (`student_mode: false`) is for verifying student predictions only. Keep `stance` in frontmatter for orchestrator selection (catalog may warn on code skills—ignore). Pair with **execution-trace** when the focus is general register state, not stack layout.
