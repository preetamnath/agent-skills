---
name: structure-prose
description: "Reshape one prose block into a list or table when it fuses several independent rules, keeping each claim's wording. TRIGGER when: user says 'break this up', 'wall of text', 'should this be a list/bullets', 'structure this paragraph'; a dense block buries rules a reader needs to jump to."
---

# Structure Prose

Primitive: **FUSED-BLOCK** — does the block state several independent rules, or one connected chain of reasoning?

## Steps

1. **Count the block's distinct claims** — rules, facts, or cases that stand alone. 1–2 claims, or a block that already scans in one line → prose is fine; stop.
2. **Apply the fused-block test.** Independent — items make sense in any order, even after a shared setup → structure them. One chain — each sentence sets up the next (a narrative, a causal argument, an explanation that builds) → keep prose; stop.
3. **Pick the shape:**

   | Shape | When it helps |
   |---|---|
   | Plain bullets | Each item is easy to find by its opening words. |
   | Labeled bullets | A brief label makes an item easier to find. |
   | Numbered list | Order matters. |
   | Table | Items share comparable fields, and columns make them easier to compare. |

4. **Reshape, content verbatim:**
   - Move each claim into an item without changing its words.
   - For labeled bullets, use a short bold label that adds no claim.
   - Leave shrinking or clarifying to `tighten-instruction`.
5. **Test each label:** read its item without the label.
   - Remove the label if the item is just as easy to find.
   - Rename a useful label that misnames the item.
6. **Score and gate the edit.** Score confidence `0.00–1.00` that the claims remain verbatim and the new shape scans better.
   - If a caller owns a file-level gate, return the score and proposal without editing.
   - Otherwise, apply at `c ≥ 0.75`; below that, keep the prose block and report the proposal as held.
