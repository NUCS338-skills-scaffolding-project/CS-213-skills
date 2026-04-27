---
skill_id: "assembly_translation"
name: "Assembly Translation (x86-64)"
skill_type: "code"
tags: ["assembly", "x86-64", "translation", "reverse-engineering", "cs213"]
python_entry: "logic.py"
---

# Assembly Translation (x86-64)

## Description

Translates small x86-64 assembly snippets into readable, C-like pseudocode and a per-line explanation. Designed for intro systems workflows: mapping registers to variables, understanding `lea`, and interpreting arithmetic and memory operands.

## When to Trigger

- Student asks “what does this assembly do?”
- Student needs to map `mov/add/sub/lea/cmp/test/j*` into C-like logic
- Student is confused by AT&T vs Intel syntax or addressing modes like `-0x8(%rbp)`

## Inputs

`run(input: dict) -> dict`

Required keys:
- `asm` (str): multi-line assembly text

Optional keys:
- `syntax` (str): `"att" | "intel" | "auto"` (default `"auto"`)
- `include_pseudocode` (bool): include pseudocode summary (default `True`)
- `max_instructions` (int): cap parsed instructions (default `200`)

## Outputs

A dict:
- `ok` (bool)
- `syntax` (str): detected/used syntax
- `instructions` (list[dict]): normalized instruction records
- `line_map` (list[dict]): per input line: parsed instruction + explanation
- `pseudocode` (str): C-like pseudocode (if requested)
- `assumptions` (list[str])
- `warnings` (list[str])
- `errors` (list[str])

## Usage

```python
from logic import run

asm = """
push rbp
mov rbp, rsp
sub rsp, 16
mov DWORD PTR [rbp-4], edi
lea eax, [edi+edi*2]
add eax, 7
"""

out = run({"asm": asm, "syntax": "intel"})
print(out["pseudocode"])
print(out["warnings"])
```

## Notes

- **Scope**: heuristic translation for *small teaching snippets*; not a decompiler.
- **Edge cases**: mixed syntax, implicit operand sizes, flags-based branches (`jle`, `jne`) without full CFG, and unknown memory types (byte/word/dword/qword) may produce warnings.
