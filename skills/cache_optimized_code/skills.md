---
skill_id: "cache-optimized-code"
name: "Cache Optimized Code"
skill_type: "code"
tags: ["cs213", "c", "performance", "memory"]
course_types: ["cs"]
learning_goal_tags:
  - "understand-memory-hierarchy"
  - "optimize-performance"
  - "analyze-code-efficiency"
trigger_signals:
  - "is my code optimized?"
  - "slow-code"
  - "loop-optimization"
  - "cache-miss"
  - "performance-issue"
chip_icon: "🧠"
python_entry: "logic.py"
version: "0.1.0"
---

# Cache Optimized Code

## Description

Acts like a TA by guiding students to understand how their code interacts with the cache. Uses Socratic questioning, hints, and step-by-step reasoning to help students discover optimizations related to spatial and temporal locality instead of directly giving answers.

## When to Trigger

- User asks why their code is slow or inefficient
- User provides loop-heavy or array-based code
- User mentions cache, memory locality, or performance optimization

## Inputs

- C/C++ code snippet (loops, arrays, matrix operations)
- Optional description of the performance issue
- Optional: user skill level (to adjust hint depth)

## Outputs

- Guided questions about memory access patterns
- Incremental hints (not full solutions immediately)
- Explanations of cache concepts when needed
- Suggested optimizations only after reasoning steps

## Usage

```python
from logic import run
result = run({
    "code": "for (int i = 0; i < n; i++) {...}",
    "mode": "guided"  # optional: guided | hint | explain
})
print(result)
```
