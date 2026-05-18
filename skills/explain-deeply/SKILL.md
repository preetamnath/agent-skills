---
name: explain-deeply
description: "Explain how a feature, flow, or concept works by grounding in source-of-truth and walking top-down with diagrams. TRIGGER when: user says explain/walk me through/ELI5/help me understand; user wants to understand how a feature, flow, or system works; user wants intuition or first principles. SKIP when: user wants a diagnosis/fix/action; user wants a one-line definition they can already apply; quick spot-check or confirmation."
---

# Explain Deeply

Read the source of truth before explaining. Walk top-down from the biggest-picture frame to the specific question, layer by layer, with diagrams as the spine.

This skill overrides default output formatting (lead-with-the-answer, bullet-first, terse fragments) while the user is building understanding. Write in paragraphs. Revert to default output when they shift to action, diagnosis, or a new subject.

## Instructions

### 1 — Reframe and ground

1. **Decide what to read.** For each check below, ask: *would reading change the explanation?* If no, skip it.
   - **Specific to this project** (a feature, function, flow, or doc in this repo) → read those files. The codebase is the source of truth, not your training.
   - **Version-sensitive or current** (a library's recent API, a current spec, a fast-moving tool) → fetch external info.
   - **General, stable concept** (e.g., "what is idempotency") → use training directly.

   The first two compose — "how does our app use Stripe's new API" needs both repo code and current docs.

2. **Restate what the user is asking, as a specific commitment.** Not "you want to know about auth" but "you want to understand how OAuth tokens flow from login through the middleware to the protected route." If their premise is wrong, say so and redirect. If they already framed it, sharpen — don't restart. For atomic definition questions ("what is a closure"), one line is enough.

### 2 — Top-down zoom

Default shape: open with the biggest-picture frame (2–4 sentences), then go layer-by-layer toward the specific question. Continue until the specific question is fully answered, in context of the bigger picture.

When the topic has no natural layers (definitions, single-mechanism concepts), compress: motivation → mechanism → example. Don't fake layers that aren't there.

Stop at the layer where the user's specific question is directly addressed. If adjacent depth would help, offer it as an optional next layer (e.g., "want me to go into how the middleware validates the token?").

## Diagrams

Visual artifacts (ASCII diagrams, sequence flows, comparison tables, file/module maps, trees) are the spine of explanations when the topic has shape that prose cannot capture.

**Diagram-helpful surfaces** — produce a diagram and let prose annotate it:
- **Spatial layout** — architecture, file/module structure, system topology
- **Sequence over time** — request/response flows, state transitions, lifecycles, pipelines
- **Hierarchy** — call trees, dependency graphs, inheritance, taxonomies
- **Parallel comparison** — two or more approaches with structured differences (use a table)
- **Connections** — who calls whom, data flow between components, event propagation
- **Layered systems** — stacks, pipelines, request-traversal-through-middleware

**No-diagram surfaces** — explain in prose, do not produce a diagram:
- **Definitions** — "what does X mean"
- **Abstract concepts with no spatial, temporal, or relational structure** — e.g., "what is a monad"
- **Cause-effect questions about phenomena where the cause is conceptual, not structural** — e.g., "why is the sky blue"
- **Single-step procedures or single-mechanism explanations** that flow naturally as prose
- **Single-fact answers** with no internal structure to render

If a query straddles both — e.g., "how does our auth flow work" (sequence) plus a sub-question "what is OAuth" (definition) — diagram the part with shape and explain the rest in prose.

The test for any diagram: *does it carry information the prose cannot, or does it merely re-render the prose into boxes?* If the latter, drop it.

## Rules

- **Name real difficulty out loud** — "this part is genuinely tricky," "nobody fully knows why" — when accurate.

- **Tie warmth to a specific moment** ("you've spotted it," "this part is tricky"), not to the act of asking ("great question!"). Test: would the warmth still make sense if they hadn't asked, or hadn't hit a hard part? If yes, it's filler.

- **Build the model, don't narrate the code.** Explain *why* the design works this way; if your structure follows the order of files, you're summarizing.

- **Limit rhetorical questions to one or two per explanation, then make assertions.**

- **When a simplification is technically wrong (not just incomplete), say so and give the correct version.**

- **React with curiosity only where the mechanism is genuinely non-obvious, not where a fancy term hides something simple.**

- **Anchor each layer to the user's question.** At each layer transition in the zoom, name how this layer answers the user's specific question. If you can't, cut the layer.

- **Define a term so the reader can apply it.** "Idempotent means safe to retry" defines a label with another label — the reader can't apply it without first knowing what "safe to retry" means. "Idempotent means calling N times produces the same result as once" gives the reader a test they can run on any operation.
