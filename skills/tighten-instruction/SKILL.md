---
name: tighten-instruction
description: "Collapse a multi-clause line — command or fact — into one positive line that reads cold. TRIGGER when: user says 'tighten this rule/fact', 'make this leaner/simpler' in a skill, CLAUDE.md, agent prompt, or rule file."
---

# Tighten Instruction

## Steps

1. **State the goal in one sentence:** what should the reader do or know after reading it?
2. **Name each line or heading's purpose.**
   - **Cut if:** the purpose is "restate the goal," "hedge," or "explain why."
   - **Rename if:** a heading misnames its content.
3. **Collapse clauses the positive form already implies.**

   Before: *"Run tests after edits. Don't skip even for small changes — small changes break things too."*
   After: *"Run tests after every edit."*
4. **Land on one positive line — in the shape the content wants:**
   - **Instruction → trigger + action:** "When X, do Y." / "Use X for Y."
   - **Fact → subject + the non-derivable part:** "X is Y, not the expected Z." / "X — the constraint/reason." (gotchas, couplings, conventions, rationale all take this shape)
   - **If it won't compress to one line:** split — it's two.
5. **Test it cold.** Read the final line without surrounding context. If you can't act on it, retighten.
