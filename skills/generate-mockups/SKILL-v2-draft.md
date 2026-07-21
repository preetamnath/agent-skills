---
name: generate-mockups
description: "Generate UI mockups as one-file HTML, no build, grounded in the project's real design language — PREVIEW a feature's screens or states, or COMPARE directions for one choice and pick. Fidelity follows the project's toolkit: high when it loads, approximate when it can't. TRIGGER when: you want a UI screen, flow, or set of states rendered, or to compare 2+ visual directions you'd judge better by seeing than by ASCII; user says 'mock this up', 'show me the screens', 'show me the states', 'show me the options', 'which looks better'. SKIP when: one direction is obviously right; the choice is logic/data/architecture, not visual; ASCII conveys it (AskUserQuestion preview); inventing one aesthetic from a blank canvas (frontend-design)."
---

# Generate Mockups

Render UI as one-file HTML, grounded in the project's real design language, so a decision is made by seeing rather than by reading prose or ASCII. Two intents, one skill:

- **Preview** — render one or more screens/states of a feature to visualize it. Keep them; iterate.
- **Compare** — render 2+ directions for a single visual choice, side-by-side, to pick one.

## Protocol

### Step 1 — Frame and checkpoint

Decide the shape of the request:
- **Intent** — PREVIEW (screens/states, keep them) or COMPARE (directions for one choice, pick one).
- **Count** — PREVIEW: one entry per screen/state. COMPARE: 3 directions by default, 5 max.

Print the planned list (one line each — the screen, or the direction + its bet) and confirm via `AskUserQuestion` ("Generate these" / "Adjust") before spending generation effort.

### Step 2 — Ground

Get the project's real design language — don't invent it:
- **Read `meta/DESIGN.md` if it exists.** It carries the facts: toolkit, tokens, components, styling model, and per-library docs pointers. If it lists multiple surfaces (distinct UI contexts with different toolkits — an admin vs an extension, web vs email), use only the block for the surface you're mocking.
- **If there's no DESIGN.md:**
  - **Grounding will be reused** → offer to **invoke the `map-design-language` skill via the Skill tool** to research and write one — a durable doc pays off.
  - **One-off, non-trivial codebase** → dispatch a read-only `general-purpose` subagent to return the facts block: the styling system (CSS vars → copy `var(--…)` names; Tailwind → reuse classes/theme; plain CSS → copy rules), the tokens in use, and the sibling UI the mockup must sit beside.
  - **One-off, trivial one-file case** → read those facts inline yourself.
- **If there's no design to ground in at all** (a brand-new, blank-canvas app), say so and suggest `frontend-design` — then proceed if the user still wants mockups.

**Derive fidelity from whether the real toolkit can load** (see [Fidelity](#fidelity)) so you set the right expectation before drawing.

COMPARE only: invoke the `jtbd` skill via the Skill tool (skip its Steps and Job-frame output) and write the job this choice serves as one job-story — reuse the caller's when one is already drafted in context. Then name the [divergence axes](#divergence-axes) that matter for this choice.

### Step 3 — Generate

Scale effort to stakes:
- **Simple / low-ambiguity** → single pass, you author every mockup.
- **Many screens or high-ambiguity COMPARE** → fan out parallel `general-purpose` subagents, one mockup each (one screen, or one axis-corner direction), carrying the grounded facts, the [lens kit](#lens-kit), and (COMPARE) the drafted job-story. Each returns its HTML file path, its filled [per-mockup card](#per-mockup-card), and confirmation it cleared the Step 4 QC floor.

Render constraints:
- **One HTML file per artifact, no build step.** Source styles in precedence order — the toolkit is the design language; don't hand-approximate what can load for real:
  1. **Toolkit CDN**, when one loads without a build. A CDN-linked artifact renders online-only — note that on it.
  2. **Project's own CSS, copied in** — never linked by path: a live link drifts with the app and breaks the point-in-time record; app-server paths are dead under `file://`.
  3. **Hand-written inline CSS from the known tokens** — whenever the toolkit can't load ([Fidelity](#fidelity): Approximate), even if project CSS was copied in: match layout and hierarchy, and take component props from the library's docs (DESIGN.md links them) rather than inventing them.
- **No decorative external assets** — placeholder boxes for images; no stock photos, icon-pack CDNs, or fonts the project doesn't load itself.
- Responsive at 375 / 768 / 1024 / 1440. Where layout changes across them, tab the widths rather than making the reader resize and compare from memory.

### Step 4 — Judge

- **QC floor (always)** — text contrast ≥ 4.5:1, interactive hit area ≥ 44×44, renders across the breakpoints, no decorative external assets. Fix before handoff.
- **COMPARE only** — critique each direction with the [lens kit](#lens-kit) and clear its anti-patterns. Then score on weighted criteria, **job-fit weighted highest**: job-fit against the drafted job-story · usability (Nielsen) · visual quality (Refactoring UI) · fit with the existing system · feasibility/risk; sanity-check with an impact/effort pass. State the verdict — top pick + why.

### Step 5 — Assemble and open

You assemble the final artifact yourself — when Step 3 fanned out, merge the returned files into it (isolate each screen, e.g. `<iframe srcdoc>` or scoped wrappers, so styles don't collide), re-run the QC floor on the merged page, then discard the subagent files: they're inputs, not deliverables.

- **PREVIEW** → one artifact, not a file per screen or state; each carries its [per-mockup card](#per-mockup-card). Layout follows what you're showing:
  - **Screens in a flow** → stack in flow order (1 → 2 → 3); the order is the information.
  - **One element, one variable changing** → one tabbed page, one tab per value, the element in a fixed position — differences only show when nothing else moves. Arrow keys step through.
    Common variables: state · data volume (none / one / many) · content extremes (long text, RTL) · viewport width · theme · role.
  - **Replacing UI that already ships** → show the current version beside the proposal, dimmed and labeled — or toggled at one position when the change is too small to spot side-by-side. The decision is about the delta, not the absolute.
- **COMPARE** → one `options.html`: directions side-by-side, each next to the real sibling control (and a current/failed state where one exists); each card carries its fields; the agent's **verdict on top**. The verdict pre-digests; the human still decides by seeing.

Write to the durable home, then open it:
- **In a spec context** → the `mockups/` path the caller passes (`product-interview` passes `meta/specs/NNN-slug/mockups/`); if you were pointed at an existing spec instead, use that spec's folder. Create it if missing.
- **Standalone** → `meta/mockups/NNN-name/` (number = highest existing + 1, start at 001).
- **Open** — `open <file>.html` so the user views it in their browser; never publish mockups via the Artifact tool.
- **Refining a winner** — a new run of this skill: render the variants in one new artifact in the same folder as the record it refines (reuse that folder; don't mint a new NNN); `options.html` stays frozen as the decision record.
- **Index** — a run produces one artifact, but a folder accumulates them across runs; once it holds 2+ artifacts, regenerate an `index.html` on every write — a plain list linking each file with its one-line "what it is" — and open the index instead.

### Step 6 — Outcome

- **PREVIEW** → the user reviews; while the review is live, iterate on the same artifact in place. Once the design ships, the snapshot rule applies — it's a record, not maintained code.
- **COMPARE** → the user picks one by seeing. Where the pick gets recorded depends on who called you:
  - **`product-interview` invoked you** → **return** the pick + rejected directions (with why each lost) for it to record and stamp at its Step 5 — don't write the spec yourself.
  - **Pointed directly at an existing spec** (no interview running) → write the chosen + rejected directions into its UX section and stamp the link.
- **Stamp every mockup link you write.** Wherever a mockup is linked (a spec, or a standalone record), add: *Mockups are directional, not final — they show the chosen layout and intent, not exact pixels; the real UI is built with the actual components and tokens, so spacing, color, and type may differ. If the two disagree, the design system / `meta/DESIGN.md` wins, not the mockup.*

## Rules

- **Mockups are point-in-time artifacts.** Snapshots, not living code — they may rot once the design ships; keep them as the visual record, don't maintain them.

---

## Fidelity

| Can the real toolkit load? | Fidelity | What the mockup does |
|---|---|---|
| **Yes** — free-form CSS, or a toolkit that loads without a build | **High** | renders through the real thing; ports ~1:1 |
| **No** — needs a build or install, or renders only in a vendor's sandbox (extension SDKs) | **Approximate** | conveys layout + hierarchy; exact color/type/radius come from the library at port time |

Approximate is a failure mode only when the toolkit would have loaded and you drew it by hand anyway — otherwise it still answers the layout and hierarchy questions.

## Divergence axes

Pick the axes that matter for the choice; place each direction on a different corner. A direction must differ on **≥2** axes.

| Axis | One end ↔ other end |
|---|---|
| Density | compact ↔ spacious |
| Hierarchy driver | size ↔ color ↔ space |
| Affordance | explicit buttons ↔ minimal / gestural |
| Containment | cards / borders ↔ flat / borderless |
| Disclosure | everything visible ↔ progressive |
| Convention | conventional (Jakob) ↔ novel |
| Motion | static ↔ animated |

Push past the first idea — the obvious solution is direction zero, not a real direction.

## Lens kit

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

## Per-mockup card

Each mockup carries, on its card:
- **What it is** — the screen, or the direction's bet, in one line.

COMPARE cards add:
- **Best for** — where it best serves the drafted job-story, often the *without*.
- **Rationale** — why it could win.
- **Trade-off** — what it sacrifices.
- **Risk** — what's unknown or could fail.
- **Axes** — the corners it occupies.
- **Confidence** — 0.00–1.00.

Trade-off and Risk are required — a card without a cost is not done.
