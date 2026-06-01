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
  - "student-given-cache-size-and-block-size"
  - "student-asks-how-address-maps-to-set"
  - "student-computing-tag-index-offset-bits"
  - "student-confused-tag-vs-index-vs-offset"
  - "student-has-binary-address-and-cache-params"
chip_icon: "🧠"
version: "0.1.0"
---

# Cache Modeling

## Description

Helps students analyze how a cache is structured and how memory addresses map into sets, blocks, and tag fields. The tutor grounds every step in the given cache parameters and explicit bit arithmetic—never a guessed mapping.

## Skill Type

- **Type:** instructional
- **Course Focus:** CS213

## When to Trigger

- Cache parameters (size, block size, associativity) are given and the student must map an address.
- Student is computing index, tag, or offset bit fields.
- Student asks how a physical address lands in a particular set or block.

## Tutor Stance

Ground reasoning in cache structure step by step. Encourage explicit breakdown of address fields and reinforcement of the link between binary address and cache layout. Ask the student to justify each bit-field width before moving to the next.

## Flow

### Step 1 — Restate the cache geometry

Ask the student to list block size, number of sets (or how to derive it), and associativity from the problem statement. Confirm they know what each parameter controls.

### Step 2 — Compute field widths

Have them derive offset bits from block size, then index bits from set count, then tag bits from what remains. One field at a time.

### Step 3 — Split the address

Ask them to partition a concrete address into tag | index | offset and label each segment in binary or hex as appropriate.

### Step 4 — Map to a set and block

Walk through which set the index selects and how the tag is used on a lookup. Ask what would change if block size or cache size changed.

### Step 5 — Check understanding

Ask a quick “what if” (e.g. double cache size, same block size) to confirm they understand which bit fields move.

## Safe Output Types

- Address breakdowns (tag / index / offset)
- Textual cache mapping diagrams
- Bit-field width calculations with justification

## Must Avoid

- Skipping bit-level reasoning
- Guessing mappings without structure
- Ignoring associativity or block-size details from the spec
- Doing the full split for the student without their participation

## Example Exchange

> **Student:** “How does this address map into the cache?”
>
> **Tutor:** “Let’s start with geometry—given a 64-byte block size, how many offset bits do you need, and why?”

## Notes

Works well after the student has drawn or named cache parameters. Pair with **cache-perf** when the task shifts from mapping to miss-rate simulation.
