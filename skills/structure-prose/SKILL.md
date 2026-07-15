---
name: structure-prose
description: "Reshape one prose block into a labeled list or table when it fuses several independent rules — form only, content verbatim. TRIGGER when: user says 'break this up', 'wall of text', 'should this be a list/bullets', 'structure this paragraph'; a dense block buries rules a reader needs to jump to."
---

# Structure Prose

Primitive: **FUSED-BLOCK** — does the block state several independent rules, or one connected chain of reasoning?

## Steps

1. **Count the block's distinct claims** — rules, facts, or cases that stand alone. 1–2 claims, or a block that already scans in one line → prose is fine; stop.
2. **Apply the fused-block test.** Independent — the items parse in any order, none leans on the previous sentence → structure them. One chain — each sentence sets up the next (a narrative, a causal argument, an explanation that builds) → keep prose; stop.
3. **Pick the shape:** labeled bullets (default) · numbered list when order is the content · table when the items share 2+ fields.
4. **Reshape, content verbatim.** Give each item a label naming its rule — a bold lead-in, or the table's first column. Move words, don't rewrite them; shrinking or clarifying a line is `tighten-instruction`'s job, a separate pass.
5. **Test:** can a reader jump straight to the one rule they need without reading the whole block? If not, the labels name topics, not rules — rename them.
