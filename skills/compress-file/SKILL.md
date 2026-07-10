---
name: compress-file
description: "Compress one instruction file to the leanest STRUCTURE that still delivers its purpose — dissolve sections that restate others, fold unique survivors into the section that governs them. TRIGGER when: user says 'why is this so long', 'strip the fat', 'de-duplicate this skill/doc', 'these sections overlap'."
---

# Compress File

Cut structure, not meaning — the file must still deliver its purpose, in fewer lines.

## Steps

### Step 1 — Pin the purpose + its invariants

State in one line what the file is for. List every distinct instruction it must still deliver — the checklist you prove against in Step 4.

### Step 2 — Find and remove structural fat

Map which sections restate the purpose, the description, or each other. Judge each overlap:

- **CUT** — content another section or the description already carries.
- **FOLD** — unique content in the wrong home → move it into the section that governs it, then delete the emptied section.

invoke the `tighten-instruction` skill via the Skill tool; tighten each survivor in place. Leave the file's output-contract or skeleton near-untouched — it's the product.

### Step 3 — Confirm, then apply

Show the plan, then on approval (`AskUserQuestion`) `Edit` — never auto-apply, even at confidence 1.0.

```
**Compression plan — <file>**
Purpose (must survive): <one line>
- CUT:  <section/line> — already in <where>
- FOLD: <content> → <target section>
```

Write `Nothing to compress — already lean.` when there's nothing to change.

### Step 4 — Prove and quantify

Every Step 1 invariant must survive or be an approved CUT. Report net lines and words removed, and the percentage.
