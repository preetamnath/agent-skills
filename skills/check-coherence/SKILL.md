---
name: check-coherence
description: "Cold-read one changed instruction file for clarity and internal coherence. TRIGGER when: user asks for a cold read, coherence check, or final clarity-and-coherence pass after edits."
---

# Check Coherence

Primitive: **READS-COHERENT** — does the complete file read clearly and agree with itself?

## Steps

1. Read the complete file cold.
2. Find instructions that are unclear, conflict with another instruction, or depend on a missing input or step.
3. For each finding, cite the relevant passages and propose the smallest meaning-preserving fix.
4. Score confidence `0.00–1.00` that the problem is real and the fix preserves meaning. Return scored findings when the caller owns the file-level gate; otherwise apply at `c ≥ 0.75` and hold below it.
5. If the first pass edits the file, repeat Steps 1–4 once, then stop.
