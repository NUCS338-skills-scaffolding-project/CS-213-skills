# Welcome to the Skills Scaffolding Project — Team Guide

This guide walks you through everything you need to do as a course team.
Follow these steps in order and reach out to the Admin if you get stuck.

> **What changed in this version:** the YAML header now includes a few new fields (`stance`, `course_types`, `learning_goal_tags`, `trigger_signals`), `logic.py` is now **optional** for instructional skills, and there are short naming conventions for `skill_id` and `name`. Existing skills will keep working — they just generate warnings until they're updated. Search for "**NEW**" through this guide to find every change.

---

## Your Task Checklist

- [ ] Generate your repository from the Admin template
- [ ] Define your course-level `metadata.yaml`
- [ ] Identify your skill type (instructional or code)
- [ ] Create `skills/` folders for every unique learning objective
- [ ] Write `skills.md` using the mandatory schema
- [ ] **NEW** — Pick the right `stance` (instructional skills only)
- [ ] **NEW** — Tag your skill with `learning_goal_tags`
- [ ] Implement `logic.py` for code skills (optional for instructional)
- [ ] Verify everything runs locally before pushing

---

## Step 1 — Set Up Your Repository

> Do NOT create a new repo from scratch.

1. Go to the `skill-standard-template` repo in the Organization
2. Click the green **"Use this template"** button
3. Name your repo using your course ID — e.g. `phil-270-skills`
4. Set the **Owner** to the Organization *(not your personal account)*
5. Click **"Create repository"**

---

## Step 2 — Create Your Course Metadata

In the root of your repo, create a file called `metadata.yaml`:

```yaml
course_id: "PHIL-270"
course_name: "Introduction to Ethics"
course_type: "humanities"           # "humanities" or "cs"
spoc_contact: "advisor@example.com"
skills_used: ["counter-example", "claim-verification"]
```

Notes:
- `course_id` becomes the `owner_team` identifier for every skill in this repo when the catalog is built.
- `spoc_contact` becomes the `owner_contact` field in the catalog — used by the orchestrator to attribute skills to a team.
- `skills_used` is a list of skills you've adopted from *other* teams' repos. Yours go under `/skills/` and are picked up automatically.

---

## Step 3 — Understand Your Skill Type

This project supports **two types of skills**.
Read carefully and identify which type applies to your course:

---

### Type 1 — Instructional Skills
**For:** Humanities, tutoring, Socratic questioning, guided learning

- Your skill is a **teaching or tutoring approach**.
- `skills.md` documents the teaching flow.
- **NEW:** `logic.py` is **optional**. If your skill is a pure prompt flow (e.g., asking the student to paraphrase, or surfacing assumptions), you don't need a `logic.py` at all. If your skill needs executable logic (text analysis, scoring, keyword detection), include a `logic.py`.

**Examples — when to include a `logic.py` for an instructional skill:**
- Text analysis *(scanning student essays for tone or complexity)*
- Response scoring *(checking if answers hit key concepts)*
- Prompt generation *(dynamically generating Socratic questions)*
- Keyword detection *(flagging when a student is off topic)*
- Progress tracking *(logging how far a student is through a skill)*

**Example skills:**
- *Bound Scope* — helping students avoid overengineering (no logic.py needed)
- *Counter-Example* — pressure-testing a claim with a probe (no logic.py needed)
- *Off-Topic Detector* — flags a drifting essay (would have a logic.py)

---

### Type 2 — Code Skills
**For:** CS courses, reusable Python logic, algorithms, utilities

- Your skill is a **reusable Python function or module**.
- `logic.py` is **required** and exposes a `run(input: dict) -> Any` function.
- `skills.md` documents how to use the code.
- Focus on: inputs, outputs, usage examples, edge cases.

**Example skills:**
- *Sorting Algorithm* — reusable sort function
- *Input Validator* — checks and cleans user input
- *Graph Traversal* — BFS/DFS implementation

---

## Step 4 — Develop Your Skills

For **every skill** your course contributes:

### 4a — Create the Skill Folder

Inside `/skills/`, create a folder named after your skill:

```
/skills/your-skill-name/
```

The folder name must match the `skill_id` in your `skills.md` (lowercase, kebab-case).

### 4b — Create skills.md

Every skill needs a `skills.md`. The YAML header at the top is **mandatory** — your push will be rejected without it.

#### For Instructional Skills:

```yaml
---
skill_id: "counter-example"          # ≤ 18 chars, kebab-case
name: "Counter-Example"              # human-readable, no trailing "Skill"
skill_type: "instructional"
stance: "socratic"                   # NEW — see Step 5
tags: ["essay", "argument", "kant"]
course_types: ["humanities"]         # NEW — subset of ["cs", "humanities"]
learning_goal_tags:                  # NEW — see Step 6
  - "construct-arguments"
  - "engage-objections"
trigger_signals:                     # NEW — optional; helps the orchestrator route
  - "student-defending-first-position"
chip_icon: "🔁"                      # OPTIONAL — single emoji for the UI
version: "0.1.0"                     # OPTIONAL — semver, defaults to "0.1.0"
# python_entry omitted — this skill has no logic.py
---

# Counter-Example

## Description
What does this skill do? Keep it to 2-3 sentences.

## When to Trigger
- Trigger condition 1
- Trigger condition 2

## Tutor Stance
Non-negotiable rules for how the tutor should behave when this skill is active.

## Flow
### Step 1 — Surface the claim
Describe what the tutor does.

### Step 2 — Offer a probe
Describe what the tutor does.

## Safe Output Types
What the tutor IS allowed to produce.

## Must Avoid
What the tutor must NEVER do.

## Example Exchange
> **Student:** "Example student message"
>
> **Tutor:** "Example tutor response"
```

#### For Code Skills:

```yaml
---
skill_id: "c-debugger"               # ≤ 18 chars, kebab-case
name: "C Debugger"                   # human-readable, no trailing "Skill"
skill_type: "code"
tags: ["cs343", "c", "coding"]
course_types: ["cs"]                 # NEW
learning_goal_tags:                  # NEW
  - "debug-systematically"
  - "interpret-error-messages"
trigger_signals:                     # NEW — optional
  - "compile-error"
  - "segfault"
chip_icon: "🐛"                      # OPTIONAL
python_entry: "logic.py"             # REQUIRED for code skills
version: "0.1.0"
---

# C Debugger

## Description
What does this skill do? Keep it to 2-3 sentences.

## When to Trigger
- Trigger condition 1
- Trigger condition 2

## Inputs
Describe what inputs the function expects.

## Outputs
Describe what the function returns.

## Usage
```python
from logic import run
result = run({"key": "value"})
print(result)
```

## Notes
Any additional notes for teams importing this skill.
```

### 4c — Create logic.py

#### For Code Skills (REQUIRED)

```python
# logic.py — Reusable skill logic
# Make it modular so other teams can import it

def run(input):
    """
    Main entry point for this skill.
    :param input: dict of input parameters
    :return: result
    """
    return f"Skill executed with input: {input}"
```

#### For Instructional Skills (OPTIONAL)

If your instructional skill needs no executable logic, **omit `logic.py` entirely** and remove the `python_entry` line from your YAML header. Don't ship empty stub files.

If your instructional skill *does* need helpers (text analysis, scoring, etc.), include `logic.py` with the same `run(input)` shape as code skills. The orchestrator will call it as a helper alongside running the `skills.md` flow.

> 💡 Make your functions modular and well documented
> so other teams can easily import and reuse them.

---

## Step 5 — Pick the Right Stance (Instructional Skills Only) **NEW**

Every instructional skill declares a `stance` in its YAML header. The stance tells the orchestrator and the tutor *how* this skill talks to the student. There are four:

| Stance | One-liner | Use it when… | Example skills |
|--------|-----------|---------------|----------------|
| **`socratic`** | The system asks back instead of answering — the student does the thinking by responding to guided questions. | Your skill's core move is "make the student articulate something they haven't yet." | `ask-for-paraphrase`, `counter-example`, `assumption-surfacing`, `ask-for-prediction` |
| **`hint`** | The system gives a partial answer or directional pointer that moves the student forward without solving for them. | Your skill is explicitly "give them something" — when asking back has stopped being productive. | `give-conceptual-hint`, `give-structural-hint`, `give-contrastive-hint` |
| **`reframe`** | The system restates the situation in different terms (analogy, concrete trace, alternative angle) to unstick a stuck framing. | Your skill changes *how* the student is thinking about the problem, without giving the answer or asking a new question. | `reframe-with-analogy`, `reframe-with-trace` |
| **`meta`** | The system shifts how the conversation itself is operating — escalating support, fading support, redirecting requests, normalizing struggle. | Your skill acts on the tutoring process rather than producing content. | `escalate-hint-level`, `fade-support`, `redirect-direct-solution`, `normalize-struggle` |

If your skill seems to fit two stances, pick the one that describes its *primary* move — the one a student would notice first.

> Code skills do **not** declare a stance. Omit the field.

---

## Step 6 — Tag Your Learning Goals **NEW**

Every skill declares which learning goals it addresses, using a controlled vocabulary maintained in the registry repo at `vocab/learning_goals.yaml`.

```yaml
learning_goal_tags:
  - "construct-arguments"
  - "engage-objections"
```

**Why this matters:** the orchestrator matches assignments (which declare their own learning goals) to skills (which declare what they address). Good `learning_goal_tags` mean your skill gets surfaced when it's relevant.

**How to pick tags:**
1. Read `vocab/learning_goals.yaml` in the registry repo.
2. Pick 1–4 tags that genuinely describe what your skill helps the student do.
3. If no existing tag fits, propose a new one via PR to the registry repo. Don't invent ad-hoc tags inside your `skills.md` — the orchestrator only matches against the controlled vocabulary.

`trigger_signals` are optional but useful: short ad-hoc strings describing conversational signals that should fire your skill (`compile-error`, `student-defending-first-position`, `repeated-direct-answer-request`). The orchestrator uses them as soft hints during candidate scoring.

---

## Step 7 — Naming Conventions **NEW**

Two short conventions, applied warn-only at v1 (existing skills are grandfathered, but they'll generate warnings in the build report).

### `skill_id` — ≤ 18 characters, kebab-case
- **Why:** the orchestrator may use it as a chip label fallback when `name` is too long. Short ids also make logs, slash-commands (`/skill counter-example`), and folder names easier to scan.
- **Good:** `counter-example`, `bound-scope`, `c-debugger`, `restate-problem`
- **Too long (would warn):** `nautilus-architecture-tutor` (27), `cause-effect-between-events-skill` (33), `assumption-validation-skill` (27)
- For long names, prefer abbreviations or remove redundant suffixes. `cause-effect-between-events-skill` becomes `cause-effect-events`. `assumption-validation-skill` becomes `assumption-check`.

### `name` — clean human-readable label, **no trailing `"Skill"`**
- **Why:** `name` is what students see on chips, in the active-skill indicator, and in the commentary trace. Trailing `" Skill"` is redundant ("Counter-Example Skill" → just "Counter-Example") and makes chip rows feel templated.
- **Good:** `Counter-Example`, `Bound Scope`, `C Debugger`, `Hand Calculation Tutor`, `Restate the Problem`
- **Would warn:** `C Debugging Skill`, `Counter-Example Skill`, `Assumption Validation Skill`
- Use Title Case. Hyphens and short compound words are fine.

---

## Step 8 — Verify Before Pushing

Before pushing your changes, make sure:

- [ ] Your `skills.md` has the full YAML header at the very top
- [ ] `skill_type` is exactly `instructional` or `code`
- [ ] `skill_id` matches your folder name, is kebab-case, and is ≤ 18 chars
- [ ] `name` is clean and does **not** end with `"Skill"`
- [ ] **NEW** — `course_types` is set (subset of `["cs", "humanities"]`)
- [ ] **NEW** — `learning_goal_tags` has at least one tag from the controlled vocab
- [ ] **NEW (instructional only)** — `stance` is one of `socratic`, `hint`, `reframe`, `meta`
- [ ] **(code only)** — `logic.py` exists and exports a `run(input)` function
- [ ] **(code only)** — your Python code runs without errors locally
- [ ] Tags are relevant and descriptive
- [ ] If your instructional skill has no executable logic, you've **omitted** `logic.py` (don't ship empty stubs)

---

## Step 9 — Push Your Changes

Once everything looks good:

1. Commit your changes to the `main` branch
2. The validation rule will automatically check your `skills.md`
3. If it passes → your skill is added to the global `catalog.json` with `status: "ready"`
4. If it has missing required fields but a known owner team → it's added with `status: "stub"` (the orchestrator will show it as a disabled chip with a "your team is building this" tooltip until the gaps are filled)
5. Other teams can fetch your skill using:
```bash
   python scripts/fetch_skill.py --id skill-name
```

> **About `stub` status:** this is intentional, not punitive. Skills land in the catalog as soon as a folder appears, even before they're complete. That lets the orchestrator be built against a partial catalog and lets your skill be discovered (as a placeholder) right away. Just keep iterating until it flips to `ready`.

---

## 📁 Your Repo Structure Should Look Like This

### Humanities / Instructional Team

```
your-repo/
├── metadata.yaml
└── skills/
    ├── bound-scope/
    │   └── skills.md             ← no logic.py needed (pure prompt flow)
    ├── counter-example/
    │   └── skills.md             ← no logic.py needed
    └── off-topic-detector/
        ├── skills.md
        └── logic.py              ← has logic.py because it scans student text
```

### CS / Code Team

```
your-repo/
├── metadata.yaml
└── skills/
    ├── c-debugger/
    │   ├── skills.md
    │   └── logic.py              ← required for code skills
    └── input-validator/
        ├── skills.md
        └── logic.py
```

---

## Common Issues

| Problem | Fix |
|---------|-----|
| Push rejected | Check your `skills.md` has all required YAML fields |
| Invalid `skill_type` error | Must be exactly `instructional` or `code` |
| Missing `logic.py` error (code skill) | Code skills must include a `logic.py` |
| **NEW** — Stuck as `stub` in the catalog | Check the build report for the missing required field — usually `stance`, `course_types`, or `learning_goal_tags` |
| **NEW** — `skill_id too long` warning | Shorten the id to ≤ 18 chars (see Step 7) |
| **NEW** — `name should not end with "Skill"` warning | Drop the trailing `"Skill"` (see Step 7) |
| **NEW** — `learning_goal_tag not in vocabulary` warning | Either pick an existing tag from `vocab/learning_goals.yaml` or open a PR to add a new one |
| **NEW** — Empty `logic.py` for instructional skill | Delete it. `logic.py` is optional for instructional; only include it if your skill needs executable helpers |
| Skill not in catalog | Make sure you pushed to `main`, not another branch |
| Can't find template | Make sure you accepted your Organization invite email |
| YAML header not working | Make sure `---` is the very first line of the file |

---

## Need Help?

Reach out to us!
