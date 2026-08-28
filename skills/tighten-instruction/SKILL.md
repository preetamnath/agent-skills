---
name: tighten-instruction
description: "Make an instruction line read cold: clarify it into plain words, then tighten it to one positive line. TRIGGER when: user says 'tighten/clarify this rule/fact', 'make this leaner/simpler/clearer', 'titan instruction' in a skill, CLAUDE.md, agent prompt, or rule file."
---

# Tighten Instruction

Two passes in order: **clarify** the text into plain words, then **tighten** each distinct instruction or fact to one line — clarity first, so tightening never compresses back into jargon.

## Steps

1. **State the goal in one sentence:** what should the reader do or know after reading it?
2. **Clarify — make every phrase read cold (clear on its own).** Decompose the line into phrases; name each phrase's intended meaning and fix any that won't land:
   - **Jargon** → plain word ("down-weight" → "rank lower").
   - **Abstraction** → concrete verb/noun ("optimize for" → "rank by").
   - **Ambiguous referent** → name it ("them" / "the better one" → the actual subject).
   - **Mismatched verb** → the true actor ("pick" when you only recommend → "favor").
   - **Cryptic compression** → unpack it ("not least effort" → "not the easiest option").

   Spend length here when it buys comprehension; preserve the meaning exactly.
3. **Tighten — cut what the clear line doesn't need.** Drop any line whose only purpose is "restate the goal," "hedge," or "explain why"; keep a non-derivable rationale as a fact in Step 4. Collapse clauses the positive form already implies, and rename a heading that misnames its content. Never trade a plain word back for jargon to save space.

   Before: *"Run tests after edits. Don't skip even for small changes — small changes break things too."*
   After: *"Run tests after every edit."*
4. **Land each distinct instruction or fact on one positive line — in the shape the content wants:**
   - **Instruction → trigger + action:** "When X, do Y." / "Use X for Y."
   - **Fact → subject + the non-derivable part:** "X is Y, not the expected Z." / "X — the constraint/reason." (gotchas, couplings, conventions, rationale all take this shape)
   - **If it won't compress to one line:** split — it's two.
5. **Test it cold.** Read the final line without surrounding context — every phrase obvious, the whole line actionable. If not, redo.
6. **Score and gate the edit.** Score confidence `0.00–1.00` that the final line is clearer, tighter, and meaning-preserving. If a caller owns a file-level gate, return the score and proposal without editing. Otherwise, apply at `c ≥ 0.75`; below that, keep the current line and report the proposal as held.
