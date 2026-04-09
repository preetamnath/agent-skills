---
name: plan-runner
description: "Executes markdown plan files with checkbox items sequentially. Finds next unchecked step, executes it, logs discoveries, marks done, commits. Resumable across conversations."
---

# Plan Runner

Executes a markdown plan file with `[ ]` checkbox items. Finds the next unchecked step, executes it, marks it done, and commits. Resumable across conversations.

## When to use

When you have a plan file (`.md`) with `[ ]` checkbox items and want to execute them sequentially with checkpointing. Works for: migration plans, refactor checklists, cleanup tasks, phased implementations.

## Protocol

### Input

- **Plan file path**: the markdown file containing the plan

### Execution loop

1. Read the plan file
2. Find the first `[ ]` (unchecked) item
3. If none found: report "Plan complete" and stop
4. Read the item's description to understand the task
5. Execute the task
6. If anything unexpected is discovered during execution, append a discovery note inline, directly after the checkbox item:
   ```
   - [x] The original task description
     - Discovery: [what was found and why it matters]
   ```
7. Mark the item `[x]`
8. Commit with message: `plan: [item description summary]`
9. Return to step 1

### Coupling detection

Before committing, check:
- Does the next unchecked item touch the same files as the one just completed?
- Are there explicit ordering notes (e.g., "must land together with item N")?
- Are the items sub-bullets under a shared parent?

If any coupling is detected: pause and use `AskUserQuestion` with:
- Options: "Commit separately", "Treat as one atomic unit"
- Recommended: "Treat as one atomic unit" (coupling usually means the items should land together)

### Rules

- Execute ONE item per cycle. Don't batch unless coupling is detected and user approves.
- If an item is blocked or unclear, DON'T skip it. Use `AskUserQuestion` with options: "Clarify and proceed", "Skip this item", "Reorder plan", "Abort plan". Recommended: "Clarify and proceed".
- If an item requires a decision the plan doesn't specify, use `AskUserQuestion` with the enumerated options and a recommended choice. Do not proceed on assumptions.
- If an item includes a verification gate (e.g., "review," "test," "user approval"), do NOT mark `[x]` until the gate passes. If the gate fails, leave the item as `[ ]` and use `AskUserQuestion` with options: "Retry this item", "Skip and continue", "Abort plan". Recommended: "Retry this item".
- Discoveries go inline with the item that found them, not in a separate section.
- Always read the plan file fresh before each item — it may have been modified externally.
- Respect ordering constraints. If the plan notes dependencies, follow them.
