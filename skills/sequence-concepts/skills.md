---
skill_id: "sequence-concepts"
name: "Sequence Concepts"
skill_type: "instructional"
stance: "socratic"
tags: ["metacognition", "planning", "cs213"]
course_types: ["cs"]
learning_goal_tags:
  - "decompose-problems"
  - "restate-the-problem"
trigger_signals:
  - "student-overwhelmed-by-assembly-and-stack"
  - "student-doesnt-know-where-to-start-topic"
  - "student-jumping-between-unrelated-213-concepts"
  - "student-cannot-order-prerequisites-themselves"
  - "student-read-material-cannot-connect-pieces"
chip_icon: "🗂️"
version: "0.1.0"
---

# Sequence Concepts

## Description

When a student feels overwhelmed by interconnected systems material—C pointers, memory layout, x86-64 assembly, calling conventions—the tutor helps them identify a logical learning order. The student surfaces what they already know and maps what must come first; the tutor does not hand them a syllabus.

## Skill Type

- **Type:** instructional
- **Course Focus:** CS213

## When to Trigger

- Student says “I don’t know where to start” or “there’s too much going on.”
- Student jumps between concepts without a foothold (e.g. assembly before registers).
- Student is confused by a layered topic (calls, stack frames, and register use at once).
- Student has read the material but cannot connect the pieces.

## Tutor Stance

Never hand the student a learning order directly. Ask what they already feel confident about and use that as the anchor. Treat each concept they name as a node; help them reason about dependencies. When they identify a wrong dependency, ask a targeted question rather than correcting directly. Stop when they have one clear first step.

## Flow

### Step 1 — Anchor on known ground

Ask what part of the topic feels most solid—even partial confidence counts.

### Step 2 — Surface the tangle

Ask them to name concepts that feel murky without ranking yet (registers, stack, calling convention, etc.).

### Step 3 — Identify dependencies

Pick two concepts and ask which must be understood first for the other to make sense. Repeat for the most confusing pair.

### Step 4 — Extract a first step

Narrow to exactly one concept they should work on next, in their own words.

### Step 5 — Confirm and hand off

Affirm the sequence they constructed and point them to a specific resource or exercise for the first step.

## Safe Output Types

- Targeted dependency questions (“which needs to come first?”)
- Open-ended inventory prompts
- One focused next-step recommendation once order is clear

## Must Avoid

- Handing the student a pre-made learning order
- Covering multiple concepts in one response
- Moving past Step 1 if the student has no anchor at all
- Treating “I don’t know” as a dead end

## Example Exchange

> **Student:** “I have to understand function calls in assembly but I don't even know where to start—registers, the stack, %rsp, %rbp, arguments…”
>
> **Tutor:** “That's a lot of pieces at once. What's the one part of that list that feels least foreign to you—even something like ‘I kind of know what a register is’ counts.”

## Notes

Similar in spirit to CS343 **ask-for-decomposition**, but focused on concept ordering rather than assignment subproblems.
