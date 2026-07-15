---
name: explain-deeply
description: "Explain a feature, flow, or concept: read the source of truth, lead with the answer, and diagram each idea the answer depends on. TRIGGER when: user says explain/walk me through/ELI5/help me understand; user wants to understand how a feature, flow, or system works. SKIP when: user wants your last response restated more simply (explain-simply); user wants a diagnosis, fix, or action; user wants a one-line definition they can already apply; a quick spot-check or confirmation."
---

# Explain Deeply

Read the source of truth, lead with a standalone answer, then let ASCII diagrams of the load-bearing mental models carry the explanation. Stay concise and structured — annotate diagrams with short prose; never build a wall of text.

## Instructions

### Step 1 — Ground

1. **Decide what to read.** Skip any source below that wouldn't change the explanation:
   - **Specific to this project** (a feature, function, flow, or doc in this repo) → read those files. The codebase is the source of truth, not your training.
   - **Version-sensitive or current** (a library's recent API, a current spec, a fast-moving tool) → fetch external info.
   - **General, stable concept** (e.g., "what is idempotency") → use training directly.

   The first two compose — "how does our app use Stripe's new API" needs both repo code and current docs.

2. **Restate the question with exact scope.** Not "about auth" but "how OAuth tokens flow from login through middleware to the protected route." If the premise is wrong, say so and redirect. One line is enough for atomic definitions.

### Step 2 — Answer, then diagram the mental models

1. **Open with a standalone answer** — 2–4 sentences that resolve the question on their own.
2. **Extract the load-bearing mental models** — the 1–4 ideas the user must hold for the answer to make sense. For each one with visual shape (see [Diagrams](#diagrams)), render an ASCII diagram and annotate it with short prose; explain the rest in tight prose or a table.
3. **Stop when the specific question is answered.** Offer adjacent depth as a one-line option ("want the token-validation path too?") instead of rendering it.

## Diagrams

**Shapes worth diagramming** — produce a visual (diagram or table) and let prose annotate it:
- **Spatial layout** — architecture, file/module structure, system topology
- **Sequence over time** — request/response flows, state transitions, lifecycles, pipelines
- **Hierarchy** — call trees, dependency graphs, inheritance, taxonomies
- **Parallel comparison** — two or more approaches with structured differences (use a table)
- **Connections** — who calls whom, data flow between components, event propagation
- **Layered systems** — stacks, a request passing through middleware

**No shape — explain in prose:** definitions, abstract concepts with no spatial/temporal/relational structure, single-fact answers.

The test for any diagram: *does it carry information the prose cannot, or does it merely re-render the prose into boxes?* If the latter, drop it. For mixed queries, diagram the parts with shape and explain the rest in prose.

## Rules

- **Build the model, don't narrate the code.** Explain *why* the design works this way; if your structure follows the order of files, you're summarizing.

- **Define a term so the reader can apply it.** "Idempotent means safe to retry" defines a label with another label. "Idempotent means calling N times produces the same result as once" gives the reader a test they can run.

- **When a simplification is technically wrong (not just incomplete), say so and give the correct version.**
