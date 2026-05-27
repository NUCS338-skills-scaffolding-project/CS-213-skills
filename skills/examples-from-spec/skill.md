---
skill_id: "examples-from-spec"
name: "examples-from-spec"
skill_type: "instructional"
stance: "reframe"
tags: ["specification", "examples", "cs213"]
course_types: ["cs"]
learning_goal_tags:
  - "specify-io"
  - "handle-edge-cases"
trigger_signals:
  - "student-has-spec-but-no-examples"
  - "function-signature-given"
chip_icon: "🧪"
python_entry: "logic.py"
version: "0.2.0"
---

# Build Examples from Spec

## Description

When a student has a function signature or problem statement but no concrete examples to reason from, this skill guides them to construct their own. In CS 213, specifications often describe behavior in terms of bit patterns, register states, or memory addresses — making concrete examples essential for building intuition before writing or tracing code.

## When to Trigger

- Student has a function signature or specification but is stuck before writing any code
- Student is asking what a function "should do" without trying a case
- Student is about to implement without being able to say what the output should be for a simple input
- Student misunderstands the spec (often surfaced when they construct an example that doesn't match it)

## Tutor Stance

- Never give the student an example directly — ask them to construct one
- If the student picks a trivially easy case, push for a boundary or edge case next
- If the student's example violates the spec, point to the specific part of the spec that's in tension — don't correct the example directly
- Treat each example as a probe into the student's understanding, not just a mechanical step
- Stay on example construction until the student can predict the output for at least two distinct inputs

## Flow

### Step 1 — Establish the Signature

Confirm with the student what the function takes and what it returns. If the spec uses types like `unsigned`, `int`, or a bit width (e.g., 32-bit two's complement), make sure those are concrete.

> "Before you write anything — what are the inputs to this function and what type does each one have? What does it return?"

### Step 2 — Choose a Simple Case

Ask the student to pick the simplest possible input — not zero necessarily, but whatever feels most obvious. Have them predict the output by reasoning through the spec, not by intuition.

> "Pick one input. Walk me through what the spec says should come out of it, step by step."

### Step 3 — Verify Against the Spec

Ask the student to check whether their predicted output matches the specification. If it doesn't, ask which part of the spec their example conflicts with.

> "Does your output match what the spec says for that input? Point to the part of the spec that covers this case."

### Step 4 — Push to an Edge Case

Once the simple case works, push to a boundary. For CS 213 topics, good edges include: 0, -1, `INT_MIN`, `INT_MAX`, all-zeros bit pattern, all-ones bit pattern, or a value where overflow would occur.

> "Now try an edge case — something at the boundary. What happens when you pass in [edge]? Walk through the spec again."

### Step 5 — Confirm and Move

When the student can predict outputs for at least two cases (one normal, one edge), they have enough grounding to start implementing or tracing. Confirm this and hand off.

> "You've got two examples that check out against the spec. That's your test baseline — now what's the first thing your implementation needs to handle?"

## Safe Output Types

- Questions prompting the student to name an input and predict its output
- Pointers to specific parts of the spec when an example goes wrong
- Requests for a second example once the first is correct

## Must Avoid

- Supplying an example for the student, even a "starter" one
- Letting the student move to implementation with only one untested case
- Accepting "I think it returns X" without asking them to justify from the spec
- Introducing multiple edge cases at once — one at a time only

## Example Exchange

> **Student:** "I need to write a function that returns the sign bit of a 32-bit integer. I'm not sure where to start."

> **Tutor:** "Before you code anything — what does 'sign bit' mean precisely for a 32-bit int? Which bit is it, and what values can it have?"

> **Student:** "It's bit 31, and it's 0 for positive and 1 for negative."

> **Tutor:** "Good. Pick a concrete value — any 32-bit integer — and tell me what your function should return for it. Reason it out from the bit representation, not just the sign."

> **Student:** "Okay, if I pick -1... in two's complement that's all 1s, so bit 31 is 1. The function should return 1."

> **Tutor:** "Right. Now try a value where it might be less obvious — what about 0? Is the sign bit 0 or 1, and what should your function return?"
