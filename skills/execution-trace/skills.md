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
  - "hand-trace-needed"
  - "register-state-question"
  - "step-through-assembly"
  - "what-are-registers-after"
  - "assembly-trace-line-by-line"
chip_icon: "📋"
python_entry: "logic.py"
version: "0.2.0"
---

# Execution Trace

## Description

Supports **hand-tracing small x86-64 snippets** (Intel-style `mov` / `add` / `sub` / `push` / `pop` and `qword ptr [...]` per `logic.py`). The focus is **register and memory state over time**, plus **choosing sensible initial inputs** (argument registers, `rsp`, stack/memory slots) so the snippet behaves as intended. The tutor goes **one instruction at a time**, checks the student’s predicted state, then moves on.

This skill is for **execution / state**, not mapping assembly to C—that is **asm-translation**.

## When to Trigger

- Student wants to **step through** assembly and understand **what lives in which register** after each line.
- Student asks how **inputs** (e.g. `rdi`, `rsi`, `rdx`, stack, memory) should be set so the code does the right thing.
- Student asks for a **hand trace** or **register values** over a short listing.

## Pedagogy (must follow)

1. **No direct “answer trace.”** Do not dump the full sequence of final register values or paste the complete `after` / `delta` column for every line as your first move. Do not present the whole solution path as established fact before the student has worked each step.
2. **Line by line.** Pick **one instruction**; ask what it **reads**, what it **writes**, and what the student predicts **before vs after** for the touched locations. Confirm or nudge only after they commit a prediction (or a partial prediction).
3. **Inputs first when relevant.** If the snippet uses `rdi`/`rsi`/… or stack slots, ask what **concrete values** they want to assume (and why), and whether **`rsp`** / memory they model is consistent with `push`/`pop` and `qword` accesses. Help them **invent a test state** without choosing “magic” values for them unless they are stuck—then offer a **small example** as a hypothesis (“try arg0 = 0 and arg1 = 1—what breaks?”), not the only correct setup.
4. **Hints toward the answer.** Use questions: “Which operand is destination?” “After `add rax, rbx`, which single register did you update?” “For this `push`, what two places change?” Optionally call `logic.run` with **`student_mode: true`** so the JSON gives **scaffolding** (mnemonic, read/write names, hint strings) **without** revealing simulated `after` states.
5. **Optional verification.** Only after they trace a line (or a block), you may use full simulation **off-thread** or confirm their numbers—still frame it as “does that match what you get if you re-evaluate the source operand?” rather than “the correct value is 0x…” unless they explicitly ask for a check after trying.

## Inputs

| Key | Meaning |
|-----|--------|
| `asm` | Assembly snippet (required), Intel-style subset as implemented in `logic.py`. |
| `initial_state` | Optional `{"regs": {...}, "mem": {...}}` — 64-bit values; `rsp` defaults if absent. |
| `student_mode` | Optional `bool` (default `false`). When `true`, response omits per-step `after` / `delta` / full solution table so the agent does not leak the worked trace; includes light per-step hints instead. |

## Outputs

- **`student_mode: false`**: `steps` with `before` / `after` / `delta` / `delta_summary`, `walkthrough_table_md`, `final_state` when `ok` — suitable for **answer keys** or internal checks, **not** to paste wholesale at students.
- **`student_mode: true`**: `steps` as **hint scaffolds** only; top-level `pedagogy` marks `hints_only`. Errors list unsupported instructions as today.

## Usage

```python
from logic import run

# Student-facing scaffolding (no revealed after-states)
print(run({"asm": "mov rax, 5\nadd rax, 3\n", "student_mode": True}))

# Full internal trace (do not dump verbatim to the student as “the solution”)
print(run({"asm": "mov rax, 5\nadd rax, 3\n", "initial_state": {"regs": {"rsp": 0x1000}}}))
```
