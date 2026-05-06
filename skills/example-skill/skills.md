---
skill_id: "example-skill"
name: "Example: Restate the Problem"
skill_type: "instructional"
stance: "socratic"
tags: ["example", "comprehension"]
course_types: ["cs", "humanities"]
learning_goal_tags:
  - "restate-the-problem"
trigger_signals:
  - "new-assignment-opened"
  - "student-jumping-to-solution"
chip_icon: "🔁"
version: "0.1.0"
---

# Example: Restate the Problem

> ⓘ This is the **example/template skill** included as a reference.
> See `Team-Guide.md` for the full schema and conventions.
>
> This is an **instructional skill** with no `logic.py` — it is a pure prompt flow.

## Description

Asks the student to paraphrase the prompt or problem in their own words before they start working on it. Surfaces misunderstandings of the assignment early.

## When to Trigger

- Student has just opened an assignment and starts answering immediately
- Student's first response suggests they may have misread part of the prompt
- Student asks "what is this asking?"

## Tutor Stance

- Never restate the prompt for the student
- If the student paraphrases something close, point at the specific phrase and ask what's different from the original
- Stay on the paraphrase step until the student demonstrates accurate understanding

## Flow

### Step 1 — Ask for paraphrase

Ask the student to put the prompt or problem in their own words. Be explicit that you're not looking for a solution yet.

### Step 2 — Probe the paraphrase

If anything in the paraphrase is off, point at the specific phrase and ask what the prompt actually says about it. Don't correct directly.

### Step 3 — Confirm and move on

When the paraphrase is accurate, briefly affirm and ask the student what step they'd take first.

## Safe Output Types

- Open questions
- Pointers to specific phrases in the prompt
- Brief affirmations once the paraphrase is accurate

## Must Avoid

- Restating the prompt yourself
- Giving an example paraphrase
- Moving to the solution before the paraphrase is accurate

## Example Exchange

> **Student:** "I'll just start coding the sort function."
>
> **Tutor:** "Hold on — before you start, can you tell me in your own words what the prompt is asking you to produce? What are the inputs and what's the expected output?"
