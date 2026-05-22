---
name: tighten-instruction
description: "Collapse a multi-clause instruction into one positive line of trigger + action. TRIGGER when: user says 'tighten this rule', 'make this leaner', 'make this simpler' in a skill, CLAUDE.md, agent prompt, or style guide."
---

# Tighten Instruction

## Steps

1. **State the goal in one sentence:** what should the reader do after reading it?
2. **Name each line or heading's purpose.**
   - **Cut if:** the purpose is "restate the goal," "hedge," or "explain why."
   - **Rename if:** a heading misnames its content.
3. **Collapse clauses the positive form already implies.**

   Before: *"Run tests after edits. Don't skip even for small changes — small changes break things too."*
   After: *"Run tests after every edit."*
4. **Land on one declarative line.**
   - **Shape:** trigger + action — "Use X for Y." or "When X, do Y."
   - **If you can't:** split — it's two instructions.
5. **Test it cold.** Read the final line without surrounding context. If you can't act on it, retighten.
