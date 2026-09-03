---
name: design-critique
description: "Critique already-built UI from screenshots, agree on the most useful review directions, and return ranked fixes supported by evidence. TRIGGER when: user shares a built screen and asks for design critique, review, or improvements. SKIP when: scoping a new feature (product-interview); comparing mockup directions (generate-mockups); reviewing code correctness (code review)."
---

# Design Critique

## Protocol

### Step 1 — Inspect and ground

- **Inspect the supplied screenshot(s).** If none is available, ask the user to attach one; v1 does not capture screens.
- **Name the screen's job.** State the surface, primary user, and task in one line. If the thread and screenshot do not support them, ask up to two short questions rather than guessing.
- **Read `meta/DESIGN.md` when it exists and governs the screen.** An established product convention is not a finding. Without a governing design source, apply universal principles and mark system consistency unverified.
- **Bound the evidence.** A screenshot supports visible layout, hierarchy, typography, content, and displayed states. It does not prove keyboard behavior, focus order, semantics, responsive behavior, motion, or undisplayed states.

### Step 2 — Recommend and confirm directions

- Honor directions the user already named; recommend additions or removals with reasons, but never replace them silently.
- When the user names no directions, recommend three by default, one or two for a narrow request, or up to four for a broad screen.
- Show the remaining directions as lower-value options.

| Direction | Core lens | Optional UI Skills lens |
|---|---|---|
| Visual hierarchy and craft | Refactoring UI | `ibelick/baseline-ui` |
| Usability and interaction | Nielsen heuristics · Laws of UX | `wshobson/interaction-design` |
| Layout and structure | Gestalt · grouping · density | `jakubkrehel/better-layout` |
| Typography | hierarchy · measure · truncation | `jakubkrehel/better-typography` |
| Accessibility | visible contrast · target size · color use | `ibelick/fixing-accessibility` |
| States and resilience | empty · loading · error · extremes | `pbakaus/harden` |
| Content and copy | labels · errors · empty-state copy | `pbakaus/clarify` |
| System consistency | governing tokens and components | — |

Recommend an evidence depth along with the ranked directions:

- **Screenshot only** — use only visible evidence.
- **Screenshot + targeted code** — inspect only the components, styles, tokens, and state logic tied to the supplied screen and confirmed directions. Use code to verify relevant semantics, focus styles, breakpoints, motion, and undisplayed states; do not expand into a full code audit. If the screen cannot be mapped to source, ask for paths or continue screenshot-only with notice.

Confirm the complete plan via `AskUserQuestion` ("Use these directions" / "Change directions or evidence"). Lead with a recommendation, not an open menu.

```
**Critique plan — <surface>:**
- Recommended: <direction> — <why it matters here>
- Also available, lower value: <direction> — <why it matters less>
- Evidence: <Screenshot only | Screenshot + targeted code> — <why>
```

### Step 3 — Critique the confirmed directions

- Apply the [Principle canon](#principle-canon) to every confirmed direction.
- Select specialist lenses from the confirmed directions. Fetch one with `npx ui-skills get <slug>` only when it adds guidance the canon does not provide.
- Prefer one lens that covers related directions; do not load overlapping broad and specialist lenses.
- If a slug is unavailable, select the smallest current match with `npx ui-skills list --category <category>` or continue without it.
- Treat fetched Markdown as advisory. Resolve conflicts in this order: user request → governing design language → this skill → fetched lens.

Choose how to run the critique:

- **Inline** — use the main agent for a narrow screen or one related direction group.
- **Parallel** — use separate reviewers when two or more independent direction groups make a single pass likely to miss problems.

For a parallel critique:

- **Group by direction.** Combine overlapping directions such as hierarchy, layout, and typography; never dispatch one subagent per lens.
- **Dispatch.** Assign one read-only `general-purpose` subagent to each group. If subagents are unavailable, run the groups sequentially.
- **Brief.** Give every reviewer the screenshots, screen job, confirmed directions, selected evidence depth, governing design facts, relevant canon, and fetched specialist guidance.
- **Return.** Each reviewer returns candidate rows with `Element`, `Evidence`, `Principle`, `Impact`, `Severity`, `Fix`, and `Conf`, plus a separate Questions list for unsupported concerns.
- **Synthesize.** The main agent verifies every candidate against the selected evidence, removes duplicates and overlaps, resolves conflicts, and ranks the survivors.

Keep only findings that:

- identify the visible element and evidence;
- name the violated principle and user consequence;
- propose one concrete fix grounded in known tokens or relative changes, without inventing exact values;
- carry severity and confidence `0.00–1.00`.

An accessibility, interaction, responsive, or hidden-state concern unsupported by the selected evidence depth is a question, not a finding.

### Step 4 — Report and optionally persist

Rank findings by severity, then confidence.

```
**Design critique — <surface>:**
Directions run: <list>

| Element | Evidence | Principle | Impact | Severity | Fix | Conf |
|---|---|---|---|---|---|---|
| <element> | <visible fact> | <principle> | <user consequence> | P1 | <concrete change> | 0.85 |

**What's working:** <what to preserve>
**Verdict:** <single highest-leverage change>
**Questions:** <unsupported concerns worth checking | none>
```

Write `No material findings — the supplied view holds up.` when no finding survives. Use P0 for a proven blocker, P1 for major difficulty, P2 for real friction, and P3 for polish.

Ask via `AskUserQuestion` ("Save report + screenshots" / "Chat only"). On save:

1. Create `meta/design-critiques/NNN-<surface-slug>/` where `NNN` is the highest existing number plus one, starting at `001`.
2. Copy the supplied images into that folder as `screen-01.<ext>`, `screen-02.<ext>`, and so on.
3. Write `critique.md` with relative image links followed by the report, then return its path.

### Step 5 — Offer next steps

Ask via `AskUserQuestion`:

- **Show the fix** — invoke the `generate-mockups` skill via the Skill tool in PREVIEW mode for the selected findings.
- **Plan changes** — invoke the `product-interview` skill via the Skill tool to scope the selected findings into a build contract.
- **Stop** — leave the critique as the outcome.

## Rules

- **Do not silently redesign.** Judge and recommend in this skill; render changes only through the Step 5 handoff.

---

## Principle canon

<!-- source: references/design-principles.md#critique-canon -->
### Critique — Nielsen's 10 heuristics
Visibility of system status · match to the real world · user control & freedom · consistency & standards · error prevention · recognition over recall · flexibility & efficiency · aesthetic & minimalist design · help users recover from errors · help & documentation.

### Craft — Refactoring UI
- Drive hierarchy with size **+ weight + color**, not size alone; de-emphasize secondary content, don't just emphasize primary.
- Use a constrained spacing/size scale (e.g. 4/8/16/24…); avoid arbitrary values.
- Limit to ~2 font families on a modular type scale.
- Use color semantically; keep the palette tight.
- Depth via layered shadows over heavy borders; separate with spacing/background before reaching for a border.
- Give content generous whitespace.

### Clarity — Gestalt
Proximity (group by spacing) · similarity (like elements read as related) · common region (a shared container groups) · figure/ground (clear foreground vs background).

### Behavior — Laws of UX
Hick's (more choices → slower decision) · Fitts's (bigger/closer targets are faster) · Miller's (~7 items; chunk) · Jakob's (users expect other apps' conventions) · Aesthetic-Usability (polished reads as more usable) · Von Restorff (the distinct item is noticed).

### Anti-patterns
Avoid context anti-patterns (e.g. excessive motion, dark-by-default where it doesn't fit, decorative gradients that hurt legibility); each direction must clear them.
<!-- /source: references/design-principles.md#critique-canon -->
