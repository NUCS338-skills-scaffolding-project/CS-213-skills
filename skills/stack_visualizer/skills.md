---
skill_id: "stack_visualizer"
name: "Stack Visualizer (Frame Layout)"
skill_type: "code"
tags: ["stack", "x86-64", "rbp", "rsp", "memory", "visualization", "cs213"]
python_entry: "logic.py"
---

# Stack Visualizer (Frame Layout)

## Description

Builds a stack-frame visualization (addresses, offsets, and likely meanings) from register values (`rsp`, `rbp`) plus a simplified memory map. Useful for explaining function prologues/epilogues, locals at negative offsets, and saved return addresses.

## When to Trigger

- Student asks “what does the stack look like right now?”
- Student is confused about `push rbp; mov rbp, rsp; sub rsp, ...`
- Student needs help interpreting memory references like `-0x8(%rbp)` or `[rbp-8]`

## Inputs

`run(input: dict) -> dict`

Required keys:
- `regs` (dict[str,int]): must include `rsp`; `rbp` recommended

Optional keys:
- `mem` (dict[int,int]): qword map address -> 64-bit value (default `{}`)
- `word_size` (int): bytes per slot (default `8`)
- `max_slots` (int): maximum number of slots to include (default `64`)
- `label_hints` (dict[int,str]): address -> label to override guesses (default `{}`)

## Outputs

A dict:
- `ok` (bool)
- `frame` (dict): basic frame info (`rsp`, `rbp`, bounds)
- `slots` (list[dict]): each slot has:
  - `addr` (int), `offset_from_rbp` (int|None), `value` (int|None)
  - `label` (str|None): guessed label like `"saved_rbp"`, `"return_address"`, `"local[-8]"`
- `warnings` (list[str])
- `errors` (list[str])

## Usage

```python
from logic import run

out = run({
  "regs": {"rsp": 0x1000, "rbp": 0x1010},
  "mem": {
    0x1000: 0x0,                 # local
    0x1008: 0x0,                 # local
    0x1010: 0x2020,              # saved rbp
    0x1018: 0x400123,            # return address
  }
})
for slot in out["slots"]:
  if slot["label"] in ("saved_rbp", "return_address"):
    print(slot)
```

## Notes

- If `rbp` is missing or zero, the visualizer falls back to showing a window starting at `rsp`.
- This skill intentionally uses a simplified memory model (qword slots), suitable for CS-213 teaching examples.
