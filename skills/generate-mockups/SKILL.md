---
name: generate-mockups
description: "Generate grounded UI mockups as self-contained HTML — PREVIEW a feature's screens, or COMPARE directions for one choice and pick — using the project's real design tokens. Fidelity is approximate by design, not pixel-perfect. TRIGGER when: you want a UI screen/flow rendered, or to compare 2+ visual directions you'd judge better by seeing than by ASCII; user says 'mock this up', 'show me the screens', 'show me the options', 'which looks better'. SKIP when: one direction is obviously right; the choice is logic/data/architecture, not visual; ASCII conveys it (AskUserQuestion preview); inventing one aesthetic from a blank canvas (frontend-design)."
---

# Generate Mockups

Render UI as self-contained HTML, grounded in the project's real design language, so a decision is made by seeing rather than by reading prose or ASCII. Two intents, one skill:

- **Preview** — render one or more screens/states of a feature to visualize it. Keep them; iterate.
- **Compare** — render 2+ directions for a single visual choice, side-by-side, to pick one.

## When to use

YES: you want to see a screen or flow rendered for real; or a UI choice has 2+ viable visual directions whose difference is *rendered* (color, fill, depth, type, density, control idiom, spatial relation) and hard to judge in monospace.

NOT this if:
- one direction is obviously right — don't manufacture options.
- the choice is logic, data, or architecture — not visual.
- the difference is structure/order/presence that ASCII conveys → `AskUserQuestion`'s `preview` field.
- you're inventing one distinctive aesthetic from a blank canvas → `frontend-design`.

This skill is grounded and in-context: it fits mockups into an existing UI. Fidelity is **approximate by design** — close enough to decide or preview, not a pixel-perfect reproduction of a component library.

## Protocol

### Step 1 — Frame and checkpoint

Decide the shape of the request:
- **Intent** — PREVIEW (screens/states, keep them) or COMPARE (directions for one choice, pick one).
- **Count** — N ≥ 1. PREVIEW: one row per screen/state. COMPARE: 3 directions by default, 5 max.

Print the planned list (one line each — the screen, or the direction + its bet) and confirm via `AskUserQuestion` ("Generate these" / "Adjust") before spending generation effort.

### Step 2 — Ground

Get the project's real design language — don't invent it:
- **Read `meta/DESIGN.md` if it exists.** It carries the facts: toolkit, tokens, components, styling model, and per-library docs pointers.
- **If it lists multiple surfaces** (distinct UI contexts with different toolkits — an admin vs an extension, web vs email), identify which surface you're mocking and use **only its block**. Most projects have one implicit surface; then there's just one set of facts.
- **If there's no DESIGN.md,** either **invoke the `map-design-language` skill via the Skill tool** to research and write one (offer this when the grounding will be reused — a durable doc pays off), or, for a one-off mockup, derive the facts from the codebase: the styling system (CSS vars → copy `var(--…)` names; Tailwind → reuse classes/theme; plain CSS → copy rules), the tokens in use, and the sibling UI the mockup must sit beside — dispatch a read-only `general-purpose` subagent to return that facts block on a non-trivial codebase, or read it inline for a trivial one-file case.
- **If there's no design to ground in at all** (a brand-new, blank-canvas app), say so and suggest `frontend-design` — then proceed if the user still wants mockups.

**Derive fidelity from the styling model** (see [Fidelity](#fidelity)) so you set the right expectation before drawing.

COMPARE only: name the [divergence axes](#divergence-axes) that matter for this choice; each direction must differ on ≥2 axes and make a different bet. Skip the obvious default as direction zero.

### Step 3 — Generate

Scale effort to stakes:
- **Simple / low-ambiguity** → single pass, you author every mockup.
- **Many screens or high-ambiguity COMPARE** → fan out parallel `general-purpose` subagents, one mockup each (one screen, or one axis-corner direction), carrying the grounded facts and the [lens kit](#lens-kit). Each returns its HTML file path, its filled [per-mockup card](#per-mockup-card), and confirmation it cleared the Step 4 QC floor.

Render constraints:
- One **self-contained** HTML file per artifact — all CSS inline, no build.
- **No external assets** — CSS placeholder boxes for images; no network fonts unless the project's own stack loads them.
- **Match the surface's styling model.** Free-CSS surface → use its real tokens. Prop-constrained library (MUI/Chakra/Polaris/an SDK) → approximate the components in HTML for layout and hierarchy; **do not invent library props** — the exact look comes from the library at port time; point to its docs (from DESIGN.md) for real props.
- Responsive at 375 / 768 / 1024 / 1440.

### Step 4 — Judge

- **QC floor (always)** — text contrast ≥ 4.5:1, interactive hit area ≥ 44×44, renders across the breakpoints, no external assets. Fix before handoff.
- **COMPARE only** — critique each direction with the [lens kit](#lens-kit), run the anti-pattern filter, then score against the [rubric](#scoring-rubric) and form a verdict (top pick + why).

### Step 5 — Assemble and open

- **PREVIEW** → lay the screens out in flow order (screen 1 → 2 → 3); each carries its [per-mockup card](#per-mockup-card).
- **COMPARE** → one `options.html`: directions side-by-side, each next to the real sibling control (and a current/failed state where one exists); each card carries its fields; the agent's **verdict on top**. The verdict pre-digests; the human still decides by seeing.

Write to the durable home, then open it:
- **In a spec context** → the `mockups/` path the caller passes (`product-interview` passes `meta/specs/NNN-slug/mockups/`); if you were pointed at an existing spec instead, use that spec's folder. Create it if missing.
- **Standalone** → `meta/mockups/NNN-name/` (number = highest existing + 1, start at 001).

Open with `open <file>.html` so the user views it in their browser. If refining a COMPARE winner, split it into a fork ledger: `{name}_1.html` → `{name}_1_1.html`.

### Step 6 — Outcome

- **PREVIEW** → the user reviews, iterates, or keeps the screens.
- **COMPARE** → the user picks one by seeing. If `product-interview` invoked you, **return** the pick + rejected directions (with why each lost) for it to record and stamp at its Step 5 — don't write the spec yourself. Only when pointed directly at an existing spec (no interview running) do you write the chosen + rejected directions into its UX section and stamp the link.
- **Stamp every mockup link you write.** Wherever a mockup is linked (a spec, or a standalone record), add: *Mockups are directional, not final — they show the chosen layout and intent, not exact pixels; the real UI is built with the actual components and tokens, so spacing, color, and type will differ. If the two disagree, the design system / `meta/DESIGN.md` wins, not the mockup.*

## Rules

- **Approximate, not exact.** A mockup is for deciding/previewing — get hierarchy, layout, and relative weight right; don't chase pixel-perfect. Exactness is the port step's job, where real library props are validated against the docs.
- **Ground in the real design.** Read `meta/DESIGN.md` if present; else derive from the codebase. Never invent tokens.
- **Surfaces are optional.** A project may have one implicit surface or several distinct ones; ground against the specific surface being mocked.
- **Match the styling model.** Free-CSS surfaces get real tokens; prop-constrained libraries get approximated components — never invented props. Point to the library's docs; don't mirror it.
- **Self-contained file.** All CSS inline, no external assets — it must open and render with zero network.
- **Diverge by construction (COMPARE).** Each direction differs on ≥2 axes and makes a different bet; skip the obvious default; cap 3 (max 5).
- **Every direction names a trade-off and a risk (COMPARE).** A card without a cost is not done.
- **Agent narrows, human decides.** Give a verdict; the pick is made by seeing.
- **Blank canvas isn't this skill.** With no existing design to ground in, suggest `frontend-design` first.
- **Proportional effort.** Fan out only for many screens or a high-ambiguity compare; a simple ask is a single pass.
- **Mockups are point-in-time artifacts.** Token approximations, not living code — they may rot once the design ships; keep them as the visual record, don't maintain them.

---

## Fidelity

Derive the expected fidelity from the surface's styling model, and set expectations accordingly:

| Styling model | Fidelity | What the mockup does |
|---|---|---|
| Free-form CSS (CSS vars, Tailwind, plain CSS) | **High** | renders faithfully; winner ports ~1:1 with the same tokens |
| Prop-constrained library whose look is inherited (MUI/Chakra/Polaris/extension SDKs) | **Approximate** | conveys layout + hierarchy; exact color/type/radius come from the library at port time |

Approximate is not a failure mode — it's the point. Chasing exactness on a prop-only library means running the real library, which is the overhead this skill exists to avoid.

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

### Per-mockup card
Each mockup carries, on its card:
- **What it is** — the screen, or the direction's bet, in one line.
- **Best for** — the job-to-be-done it serves (COMPARE).
- **Rationale** — why it could win (COMPARE).
- **Trade-off** — what it sacrifices (COMPARE).
- **Risk** — what's unknown or could fail (COMPARE).
- **Axes** — the corners it occupies (COMPARE).
- **Confidence** — 0.00–1.00 (COMPARE).

### Scoring rubric
Score each direction on weighted criteria, **JTBD-fit weighted highest**: JTBD-fit · usability (Nielsen) · visual quality (Refactoring UI) · fit with the existing system · feasibility/risk. Add an impact/effort sanity check. Skip RICE — reach is constant across visual options. State the resulting verdict (top pick + why); the human picks by seeing.
