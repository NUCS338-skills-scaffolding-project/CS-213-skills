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
  - "loop-order-comparison"
  - "matrix-traversal-question"
  - "cache-performance-from-code"
chip_icon: "📊"
version: "0.1.0"
---

# Memory Access Pattern Analysis

## Description

Analyzes how program memory access patterns interact with hardware memory layout and cache behavior.

## When to Trigger

- Comparing loop orders
- Evaluating matrix traversal efficiency
- Reasoning about locality

## Tutor Stance

- Focus on access order and stride
- Relate code structure to memory layout
- Highlight locality effects explicitly

## Flow

1. Identify memory layout (row-major / column-major)
2. Trace access pattern
3. Evaluate spatial and temporal locality
4. Predict performance impact

## Safe Output Types

- Loop traversal explanations
- Locality reasoning
- Cache behavior predictions

## Must Avoid

- Ignoring memory layout
- Treating all loops as equivalent
- Overgeneralizing performance

## Example Exchange

> Student: “Why is this loop slower?”  
> Tutor: “Let’s see how it walks through memory—are we jumping across rows or staying contiguous?”
