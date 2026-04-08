---
name: adversarial-consensus
description: Multi-agent pattern for producing airtight fixes. Parallel independent diagnosis, consensus synthesis, adversarial critique, then hardened solution.
---

# Adversarial Consensus

You are orchestrating a multi-agent debugging and review protocol. Your goal: produce a fix that survives independent diagnosis AND adversarial critique.

## When to Use

- **YES:** Multi-layer bugs (e.g. schema + router + model)
- **YES:** Framework quirks or uncertain library behavior
- **YES:** High-risk deploys (costly/hard to roll back)
- **NO:** Trivial typos, 1-line changes, zero blast radius

---

## Instructions

### Step 1: Parallel Diagnosis

1. Spin up **2 independent subagents** in parallel. Default: Sonnet. Use Opus for complex async/architectural bugs.
2. Give them ONLY the problem statement and file paths.
3. Instruct them to:
   - Read the code without communicating with each other.
   - Trace the root cause.
   - Propose a complete fix.
4. If a subagent returns unusable output, treat it as a non-vote. If only one agent returned usable output, note reduced confidence when proceeding. If both fail, abort and ask the human.

### Step 2: Consensus

Compare both diagnosis reports.

- **If they agree:** High confidence. Proceed to Step 2.5.
- **If they disagree:** Read the contested files yourself and resolve. If still ambiguous, ask the human. Once resolved, proceed to Step 2.5.
- **If both conclude not a bug:** Report findings to the human and stop.
- **If one found an extra detail:** Include it only if it concerns the same root cause and does not contradict the other agent's findings.
- **Outcome:** Produce exactly 1 unified diagnosis and fix strategy.

### Step 2.5: Draft Fix

Write concrete code implementing the unified diagnosis. This is the proposed fix that adversarial agents will review.

### Step 3: Adversarial Critique

1. Spin up **2 NEW subagents** in parallel. DO NOT reuse the diagnosis agents. Default: Sonnet. Use Opus if fix spans multiple systems or involves concurrency.
2. Provide only the proposed code changes (as a unified diff or the full updated files with changes marked), the files the fix directly modifies, and any immediate callers or tests of the modified code. **Omit all diagnostic reasoning.**
3. Instruct them to find flaws and categorize with a confidence score (0.0–1.0):
   - **P0:** Crashes or corrupts data (e.g. missing imports, typos).
   - **P1:** Serious bug in normal usage (e.g. unhandled edge cases).
   - **P2:** Edge case failure.
   - **P3:** Style or minor nit.
4. If adversarial agents disagree on severity, treat at the higher level. If confidence scores diverge significantly (>0.3 gap), note this when presenting to the human.
5. If a subagent returns unusable output, treat it as a non-vote. If both fail, abort and ask the human.

### Step 4: Harden & Output

Review the adversarial findings. **Always present findings and proposed next steps to the human before acting. Only proceed after human confirms.**

- **If P0 found (diagnosis issue):** Recommend looping back to Step 1 with the new finding.
- **If P0 found (implementation issue):** Recommend revising the code, then re-running adversarial critique from Step 3.
- **If P1 found:** Recommend incorporating into the fix. Self-review the updated code — if new issues are spotted, re-run adversarial critique (max 1 P1 re-review cycle; after that, ship with a note).
- **If P2 found:** Recommend incorporating or document why it is deferred.
- **If P3 found:** Note and defer.
- **If no issues found:** Present the clean result and recommend shipping.

---

## Constraints

- **Agent Cap:** Max 2 diagnosis + 2 adversarial agents **per loop iteration**.
- **Loop Limit:** Each return to Step 1 or Step 3 counts as one restart. Max 2 restarts before escalating to the human and stopping. When escalating, present: original problem, diagnosis reports, proposed fix, and all adversarial findings.
- **No Reuse:** Never assign the adversarial task to the original diagnosis agents.
- **Human in the Loop:** When any step requires human input (disagreements, ambiguity, escalation), use `AskUserQuestion` with structured options and a recommended choice. Never silently proceed on assumptions.

## Output Format

- **Diagnosis:** Unified root cause (1–3 sentences).
- **Fix:** Final hardened code changes.
- **Adversarial Findings:** What the adversarial agents caught (severity + confidence), and how each was addressed.
- **Deferred:** Any P2/P3 items explicitly deferred with rationale.
