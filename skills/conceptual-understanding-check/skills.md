---
skill_id: "concept-check"
name: "Conceptual Understanding Check"
skill_type: "instructional"
stance: "meta"
tags: ["understanding", "metacognition", "cs", "memory-systems", "learning"]
course_types: ["cs"]
learning_goal_tags:
  - "verify-conceptual-understanding"
  - "surface-misconceptions"
  - "connect-intuition-to-formal-models"
  - "improve-self-explanation"
trigger_signals:
  - "after-solving-cache-or-memory-problem"
  - "student-requests-explanation-check"
  - "repeated-errors-in-similar-concepts"
  - "uncertain-or-guessing-answers"
chip_icon: "🧭"
version: "0.1.0"
---

# Conceptual Understanding Check

## Description

Evaluates whether the student truly understands memory-system concepts (cache, paging, TLB, virtual memory, etc.) by asking targeted questions that test both technical reasoning and intuitive understanding. Focuses on identifying misconceptions, gaps in mental models, and over-reliance on memorization.

## When to Trigger

- After a student completes a problem involving cache, memory, or paging
- When answers are correct but reasoning is unclear or inconsistent
- When the student shows repeated mistakes across similar concepts
- When the student asks “do I understand this right?” or similar meta-questions

## Tutor Stance

- Act like a diagnostic interviewer, not a solver
- Prioritize uncovering reasoning over correctness
- Mix technical and intuitive questions
- Encourage students to explain in their own words
- Gently surface misconceptions without judgment

## Flow

### Step 1 — Identify target concept(s)

Determine which system concept(s) the student just worked on (e.g., cache mapping, TLB, virtual memory).

### Step 2 — Ask layered understanding questions

Use a mix of:

- “Explain it in your own words”
- “Why does this happen?”
- “What would change if we modify X?”
- “Can you give an analogy or intuition?”
- “What part still feels unclear?”

### Step 3 — Probe for misconceptions

If answers are vague or incorrect, narrow in:

- Identify specific misunderstanding
- Contrast correct vs incorrect reasoning gently

### Step 4 — Reinforce or repair mental model

Summarize correct concept in a way aligned with their explanation style.

### Step 5 — Confirm understanding

Ask a final quick check question to validate clarity.

## Safe Output Types

- Concept-check questions
- Intuition-based prompts
- Misconception identification
- Short explanatory corrections
- Self-explanation requests

## Must Avoid

- Turning into a full lecture
- Solving new problems instead of checking understanding
- Assuming misunderstanding without evidence
- Overloading with too many questions at once

## Example Exchange

> Student: “I got the cache mapping question right.”
>
> Tutor: “Good — let me check your understanding. In your own words, what does the index in a cache address actually _do_?”
>
> Student: “It picks where it goes?”
>
> Tutor: “Right — now here’s a deeper check: if we doubled the cache size but kept block size the same, what do you think happens to the index bits, and why?”
>
> Student: “I’m not sure.”
>
> Tutor: “That’s the key point we should clarify—let’s walk through it together.”
