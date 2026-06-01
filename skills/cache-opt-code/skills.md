---
skill_id: "cache-opt-code"
name: "Cache Optimized Code"
skill_type: "code"
tags: ["cs213", "c", "performance", "memory"]
course_types: ["cs"]
learning_goal_tags:
  - "understand-memory-hierarchy"
  - "optimize-performance"
  - "analyze-code-efficiency"
trigger_signals:
  - "student-asks-why-matrix-or-loop-is-slow"
  - "student-pastes-nested-loops-asks-locality"
  - "student-stuck-after-tried-one-loop-order"
  - "student-mentions-cache-misses-in-their-code"
  - "student-wants-nudge-on-loop-reorder-not-rewrite"
chip_icon: "🧠"
python_entry: "logic.py"
version: "0.1.0"
stance: "hint"
---

# Cache Optimized Code

## Description

Guides students to discover how their C/C++ code interacts with the cache through Socratic questioning about spatial and temporal locality. The tutor surfaces access-pattern questions and incremental hints instead of handing over rewritten optimized code.

## Skill Type

- **Type:** code
- **Course Focus:** CS213

## When to Trigger

- Student asks why their code is slow or inefficient.
- Student provides loop-heavy or array-based code.
- Student mentions cache, memory locality, or performance optimization.

## Tutor Stance

Lead with questions about memory access order and stride before suggesting loop reordering or blocking. Do not paste a fully optimized version of their program as the first response. Treat `guided` mode as the default; use `hint` or `explain` only after the student has reasoned about layout and locality.

## Inputs

| Key | Type | Description |
|-----|------|-------------|
| `code` | `str` | C/C++ snippet (loops, arrays, matrix operations); required. |
| `mode` | `str` | Optional: `guided` (default), `hint`, or `explain`. |

## Outputs

Returns a tutor-style string (not a dict) with guided questions, hints, or explanations depending on `mode`. The response references detected access patterns (e.g. row-major-friendly vs column-wise jumps) without auto-rewriting the student’s code.

## Usage

```python
from logic import run

result = run({
    "code": "for (int i = 0; i < n; i++) { for (int j = 0; j < m; j++) sum += a[j][i]; }",
    "mode": "guided",
})
print(result)
```

## Example Exchange

> **Student:** “Why is my matrix multiply so slow?”
>
> **Tutor:** “How does your inner loop walk through memory—are you visiting neighboring elements or jumping across rows? What does row-major layout in C imply about that stride?”

## Notes

Uses `logic.py` heuristics on loop index order. Does not modify student source. Keep `stance: hint` in frontmatter for orchestrator selection (catalog may warn on code skills—ignore). Safe to call repeatedly as reasoning deepens. Pair with **mem-access-pattern** for loop-order reasoning without code execution.
