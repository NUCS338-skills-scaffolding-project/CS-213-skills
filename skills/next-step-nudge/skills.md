---
skill_id: "next-step-nudge"
name: "End with Actionable Next Step"
skill_type: "instructional"
stance: "meta"
tags: ["pedagogy", "engagement", "session-management"]
course_types: ["cs", "humanities"]
learning_goal_tags:
  - "reflect-on-progress"
  - "manage-effort"
trigger_signals:
  - "tutor-response-needs-concrete-closing-action"
  - "student-says-ok-but-no-next-step"
  - "student-finished-explanation-still-unsure"
  - "session-ending-without-specific-task"
  - "student-asks-what-should-i-do-now"
chip_icon: "➡️"
version: "0.1.0"
---

# End with Actionable Next Step

## Description

Ensures every tutoring interaction ends with a clear, concrete action the student can take immediately. It keeps sessions productive and prevents vague or passive endings by guiding the learner toward momentum.

## Skill Type

- **Type:** instructional
- **Course Focus:** CS213

## When to Trigger

- At the end of every tutor response, especially after explanations.
- When a response risks ending vaguely or without direction.

## Tutor Stance

Always prioritize forward progress over completeness. Keep the next step simple, specific, and doable within a short time. Avoid overwhelming the student with multiple options. Default to one clear action unless the student explicitly asks for alternatives.

## Flow

### Step 1 — Assess current state

Briefly identify where the student is in their understanding or task (confused, partially correct, ready to apply).

### Step 2 — Choose a high-impact action

Select one concrete action that meaningfully advances progress (try a problem, write a trace, test an idea).

### Step 3 — Make it specific and immediate

Frame the action so the student can do it right away without additional clarification.

### Step 4 — Deliver as a clear closing

End the response with a direct, concise instruction or prompt.

## Safe Output Types

- A single clear task (e.g. “Try solving this…”)
- A focused prompt (e.g. “Write one example of…”)
- A small experiment or check (e.g. “Test this idea by…”)

## Must Avoid

- Vague endings (e.g. “Let me know if you have questions”)
- Multiple competing next steps
- Overly large or time-consuming tasks
- Ending without a clear action

## Example Exchange

> **Student:** “I think I understand loops, but I'm not totally sure.”
>
> **Tutor:** “You've got the basic idea of loops—they repeat a block of code—but the key is controlling how many times they run. Try this: write a simple `for` loop that prints the numbers 1 through 5, then modify it to print only even numbers.”

## Notes

Often composed with other skills; this skill only governs how the response ends.
