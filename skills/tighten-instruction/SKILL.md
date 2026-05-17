---
name: tighten-instruction
description: "Collapse a multi-clause instruction into one positive line of trigger + action. TRIGGER when: user is writing or editing an instruction in a skill, CLAUDE.md, agent prompt, or style guide; user says 'tighten this rule', 'make this leaner', 'cut this down'; a draft instruction has multiple clauses, negative carve-outs, or meta-commentary."
---

# Tighten Instruction

Turn a verbose instruction in a skill body, CLAUDE.md entry, agent prompt, or style guide into one positive line: trigger + action. Apply per instruction.

## Steps

1. **State the goal in one sentence.** What should the reader do after this instruction fires?
2. **For each line of the draft, name its purpose in plain English.** If the purpose is "restate the goal," "hedge," or "explain why" — cut it.
3. **Collapse clauses the positive form already implies.** `don't` and `skip when` are redundant when the positive trigger is precise. "Use TaskCreate when ≥ 3 steps" already implies "don't use it for < 3." Before: *"Run tests after edits. Don't skip even for small changes — small changes break things too."* After: *"Run tests after every edit."*
4. **Land on one declarative line: trigger + action.** "Use X for Y." If you can't, the instruction is two instructions — split it.

## Test

Read the final line cold; you should be able to act on it without surrounding context.
