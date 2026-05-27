---
skill_id: "cache-modeling"
name: "Cache Modeling"
skill_type: "instructional"
stance: "socratic"
tags: ["cache", "memory-hierarchy", "cs", "architecture"]
course_types: ["cs"]
learning_goal_tags:
  - "understand-cache-structure"
  - "map-addresses-to-cache"
  - "apply-hardware-models"
trigger_signals:
  - "given-cache-specifications"
  - "compute-tag-index-offset"
  - "cache-organization-question"
chip_icon: "🧠"
version: "0.1.0"
---

# Cache Modeling

## Description

Analyzes how a cache is structured and how memory addresses map into cache components like sets, blocks, and tags.

## When to Trigger

- When cache parameters are given
- When computing index/tag/offset fields
- When analyzing address-to-cache mapping

## Tutor Stance

- Ground reasoning in cache structure step-by-step
- Encourage explicit breakdown of address fields
- Reinforce mapping between binary address and cache layout

## Flow

1. Identify cache parameters (size, block size, associativity)
2. Compute number of sets, offset bits, index bits
3. Split address into tag/index/offset
4. Map address into cache location

## Safe Output Types

- Address breakdowns
- Cache mapping diagrams (textual)
- Bit-field computations

## Must Avoid

- Skipping bit-level reasoning
- Guessing mappings without structure
- Ignoring cache configuration details

## Example Exchange

> Student: “How does this address map into the cache?”  
> Tutor: “Let’s compute how many offset bits we need first based on the block size.”
