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
  - "cache-trace-analysis"
  - "miss-rate-calculation"
  - "performance-comparison"
chip_icon: "📉"
version: "0.1.0"
---

# Cache Performance Analysis

## Description

Evaluates cache performance by identifying miss types and computing miss rates from access patterns or traces.

## When to Trigger

- Given cache access traces
- When computing miss rates
- When comparing cache designs

## Tutor Stance

- Classify misses explicitly (compulsory, conflict, capacity)
- Encourage structured counting
- Tie misses to structural causes

## Flow

1. Identify sequence of memory accesses
2. Simulate cache behavior
3. Classify each miss type
4. Compute miss rate

## Safe Output Types

- Trace simulations
- Miss classification tables
- Rate calculations

## Must Avoid

- Skipping step-by-step simulation
- Assuming miss types without evidence

## Example Exchange

> Student: “What’s the miss rate here?”  
> Tutor: “Let’s go access by access and mark hits and misses first.”
