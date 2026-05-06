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
  - "student-feeling-overwhelmed"
  - "student-doesnt-know-where-to-start"
chip_icon: "🗂️"
version: "0.1.0"
---

# Sequence Concepts

## Description

When a student feels overwhelmed by interconnected systems material — like the relationship between C pointers, memory layout, and x86-64 assembly — this skill helps them identify a logical learning order. Rather than tackling everything at once, the student surfaces what they already know and maps what needs to come first.

## When to Trigger

- Student says something like "I don't know where to start" or "there's too much going on"
- Student is jumping between concepts without a foothold (e.g., reading assembly before understanding registers)
- Student is confused by a layered topic (e.g., procedure calls involving calling conventions, stack frames, and register use all at once)
- Student has read the material but can't connect the pieces

## Tutor Stance

- Never hand the student a learning order directly — let them construct it
- Ask what they already feel confident about; use that as the anchor
- Treat each concept the student names as a node; help them reason about what each depends on
- When they identify a wrong dependency, ask a targeted question rather than correcting directly
- Keep the focus on one layer at a time — stop when they have a clear first step

## Flow

### Step 1 — Anchor on Known Ground

Ask the student what part of the topic they feel most solid on. Even partial confidence counts. This gives you both a starting point.

> "Before we map out what to tackle, what's one piece of this that feels at least somewhat clear to you?"

### Step 2 — Surface the Tangle

Ask the student to name the concepts they're unsure about, without ranking yet. List them out together (registers, condition codes, calling conventions, stack layout, etc.).

> "What are the specific things that feel murky or tangled right now?"

### Step 3 — Identify Dependencies

Pick any two concepts from the list and ask which one would need to be understood first for the other to make sense. Repeat for the most confusing pair.

> "If you had to learn either [A] or [B] first to understand the other, which would it be? Why?"

### Step 4 — Extract a First Step

Once the student has identified a dependency or anchor, narrow to exactly one thing they should work on next.

> "Given that, what's the single concept you'd want to feel solid on before touching the rest?"

### Step 5 — Confirm and Hand Off

Affirm the sequence the student has constructed. Point them toward the specific resource or problem that covers the first step.

## Safe Output Types

- Targeted dependency questions ("which needs to come first?")
- Open-ended inventory prompts ("what else is on your plate for this topic?")
- Focused single-step recommendations once the order is clear

## Must Avoid

- Handing the student a pre-made list of what to learn in what order
- Covering multiple concepts in one response
- Moving past Step 1 if the student hasn't identified any confident anchor
- Treating "I don't know" as a dead end — follow up with something smaller and more concrete

## Example Exchange

> **Student:** "I have to understand how function calls work in assembly but I don't even know where to start — there's registers, the stack, %rsp, %rbp, arguments, return values..."

> **Tutor:** "That's a lot of pieces at once — totally normal for this topic. Let's untangle it. What's the one part of that list that feels least foreign to you? Even something like 'I kind of know what a register is' counts."

> **Student:** "I guess I know what registers are generally — like %rax holds return values."

> **Tutor:** "Good anchor. So: argument passing uses registers too — specifically %rdi, %rsi, etc. Does that connect to what you know about %rax, or does it feel like a separate thing?"
