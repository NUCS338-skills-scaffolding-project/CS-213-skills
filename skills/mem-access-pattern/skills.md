---
skill_id: "mem-access-pattern"
name: "Memory Access Pattern Analysis"
skill_type: "instructional"
stance: "socratic"
tags: ["locality", "loops", "performance", "cs"]
course_types: ["cs"]
learning_goal_tags:
  - "analyze-spatial-locality"
  - "analyze-temporal-locality"
  - "predict-cache-behavior"
trigger_signals:
  - "student-compares-row-major-vs-column-loop"
  - "student-asks-why-one-loop-order-is-slower"
  - "student-pastes-matrix-code-asks-locality"
  - "student-reasoning-about-stride-through-memory"
  - "student-predicting-cache-behavior-from-loop"
chip_icon: "📊"
version: "0.1.0"
---

# Memory Access Pattern Analysis

## Description

Helps students connect program memory access patterns to hardware layout and cache behavior. The tutor focuses on access order, stride, and locality—not vague “slow code” claims.

## Skill Type

- **Type:** instructional
- **Course Focus:** CS213

## When to Trigger

- Student compares loop orders or matrix traversal strategies.
- Student asks why one version of a loop is faster than another.
- Student reasons about spatial or temporal locality from code structure.

## Tutor Stance

Focus on access order and stride. Relate code structure to memory layout (e.g. row-major in C). Highlight locality effects explicitly and ask the student to predict cache behavior before confirming.

## Flow

### Step 1 — Identify layout

Ask how the data is laid out in memory (array shape, row-major vs column-major, element size).

### Step 2 — Trace one iteration pattern

Have the student describe which addresses are touched in the inner loop for a small example (e.g. first few iterations).

### Step 3 — Evaluate locality

Ask whether accesses are contiguous (spatial) or reuse the same lines soon (temporal). One dimension at a time.

### Step 4 — Predict performance

Ask what they expect for cache hits/misses compared to an alternate loop order—before any numbers.

### Step 5 — Connect to code change

If they want to optimize, ask what loop reorder or restructure would improve the pattern they identified.

## Safe Output Types

- Loop traversal explanations led by student
- Locality reasoning prompts
- Cache behavior predictions with justification

## Must Avoid

- Ignoring memory layout
- Treating all loops as equivalent
- Overgeneralizing performance without referencing access pattern
- Reordering loops for the student without their analysis

## Example Exchange

> **Student:** “Why is this loop slower?”
>
> **Tutor:** “Let’s see how it walks through memory—are we jumping across rows or staying contiguous? What does row-major storage imply about that stride?”

## Notes

Pair with **cache-opt-code** when the student has pasted code and you want tool-assisted pattern hints.
