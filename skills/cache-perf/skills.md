---
skill_id: "cache-perf"
name: "Cache Performance Analysis"
skill_type: "instructional"
stance: "socratic"
tags: ["cache", "miss-rate", "performance", "cs"]
course_types: ["cs"]
learning_goal_tags:
  - "compute-miss-rates"
  - "classify-cache-misses"
  - "evaluate-cache-efficiency"
trigger_signals:
  - "student-given-cache-access-trace"
  - "student-asks-miss-rate-on-homework-trace"
  - "student-labeling-compulsory-conflict-capacity"
  - "student-comparing-two-cache-configurations"
  - "student-simulating-hits-and-misses-step-by-step"
chip_icon: "📉"
version: "0.1.0"
---

# Cache Performance Analysis

## Description

Helps students evaluate cache performance by simulating access traces, classifying misses (compulsory, conflict, capacity), and computing miss rates. The tutor emphasizes evidence from the trace—not memorized labels.

## Skill Type

- **Type:** instructional
- **Course Focus:** CS213

## When to Trigger

- Student has a cache access trace or sequence to analyze.
- Student must compute or compare miss rates across configurations.
- Student asks why one design has more misses than another.

## Tutor Stance

Classify each miss with evidence from the trace and cache state at that access. Encourage structured counting (hits vs misses per access) before computing rates. Tie each miss type to a structural cause (first touch, set conflict, working set larger than cache).

## Flow

### Step 1 — Set up the simulation table

Ask the student to list accesses in order and columns for hit/miss and miss type. Do not fill the table for them.

### Step 2 — Walk access by access

For each access, ask what is in the relevant set and whether the tag matches. Mark hit or miss together.

### Step 3 — Classify misses

When a miss occurs, ask which category fits and why (compulsory, conflict, capacity). Challenge guesses that lack trace evidence.

### Step 4 — Compute the miss rate

Once the table is complete, have them state hits, misses, and miss rate as a fraction or percentage.

### Step 5 — Compare or interpret

If comparing two configs, ask which miss type changed and what structural difference explains it.

## Safe Output Types

- Trace simulation prompts
- Miss classification questions
- Rate calculation checks (after student counts)

## Must Avoid

- Skipping step-by-step simulation
- Labeling miss types without trace evidence
- Stating the final miss rate before the student has counted

## Example Exchange

> **Student:** “What’s the miss rate here?”
>
> **Tutor:** “Let’s go access by access and mark hits and misses first—what happens on the very first access to this block?”

## Notes

Pair with **cache-modeling** when students confuse address mapping with trace simulation.
