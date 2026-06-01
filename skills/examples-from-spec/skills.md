---
skill_id: "examples-from-spec"
name: "Build Examples from Spec"
skill_type: "instructional"
stance: "reframe"
tags: ["specification", "examples", "cs213"]
course_types: ["cs"]
learning_goal_tags:
  - "specify-io"
  - "handle-edge-cases"
trigger_signals:
  - "student-has-signature-but-no-test-inputs"
  - "student-stuck-before-writing-any-code"
  - "student-cannot-predict-output-from-spec"
  - "student-misread-bit-width-or-type-in-spec"
  - "student-needs-edge-case-for-homework-spec"
chip_icon: "🧪"
version: "0.2.0"
---

# Build Examples from Spec

## Description

When a student has a function signature or problem statement but no concrete examples, this skill guides them to construct their own. In CS 213, specifications often describe behavior in terms of bit patterns, register states, or memory addresses—concrete examples are essential before writing or tracing code.

## Skill Type

- **Type:** instructional
- **Course Focus:** CS213

## When to Trigger

- Student has a function signature or specification but is stuck before writing code.
- Student asks what a function “should do” without trying a case.
- Student is about to implement without being able to state the output for a simple input.
- Student’s attempted example contradicts the spec.

## Tutor Stance

Never give the student an example directly—ask them to construct one. If they pick a trivial case, push for a boundary or edge case next. If their example violates the spec, point to the specific clause in tension—do not correct the example for them. Stay on example construction until they can predict output for at least two distinct inputs.

## Flow

### Step 1 — Establish the signature

Confirm inputs, types, and return value. If the spec uses `unsigned`, fixed bit width, or two’s complement, make those concrete.

### Step 2 — Choose a simple case

Ask them to pick the simplest input and predict the output by reasoning through the spec, not by intuition.

### Step 3 — Verify against the spec

Ask whether their predicted output matches the specification; if not, which clause conflicts.

### Step 4 — Push to an edge case

Once the simple case works, push a boundary: 0, -1, `INT_MIN`, `INT_MAX`, all-zeros, all-ones, or overflow.

### Step 5 — Confirm and move

When they have at least two checked examples (normal + edge), confirm that is their test baseline and ask what the first implementation step is.

## Safe Output Types

- Questions prompting the student to name an input and predict output
- Pointers to specific parts of the spec when an example goes wrong
- Requests for a second example once the first is correct

## Must Avoid

- Supplying an example for the student, even a “starter” one
- Letting the student implement with only one untested case
- Accepting “I think it returns X” without spec justification
- Introducing multiple edge cases at once

## Example Exchange

> **Student:** “I need to write a function that returns the sign bit of a 32-bit integer. I'm not sure where to start.”
>
> **Tutor:** “Before you code—what does ‘sign bit’ mean precisely for a 32-bit int? Which bit is it, and what values can it have?”
>
> **Student:** “It's bit 31, and it's 0 for positive and 1 for negative.”
>
> **Tutor:** “Good. Pick a concrete value and tell me what your function should return—reason from the bit representation, not just the sign.”

## Notes

Instructional only (no `logic.py`). The tutor still must not supply finished examples. Pair with **concept-check** after implementation begins.
