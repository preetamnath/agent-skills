# Comment Sweep

The per-comment triage a sweep subagent runs over the code comments in the files a run changed. Consumers: `execute-plan` (Step 6.1), `execute-chat` (Step 5).

## Scope

Whole files, not just the comments the run wrote — a comment the run made false is one it never touched. Never the whole repo.

## Triage

```
- **Per comment**, in order:
  1. Contradicts the code it describes → rewrite it to the current fact.
  2. Fails the worth test → delete.
  3. Carries its fact but reads muddy → tighten in place.
  4. States a fact that belongs in a durable doc → return it as a `doc_candidate`, leave a one-line comment behind.
```

## Notes

- **Order is the content.** Accuracy runs first so a false comment can't reach the docs pass and become a durable fact. Worth runs before shape so a dead comment isn't tightened before being deleted.
- **The sweep stays separate from the docs pass.** `durable-docs-update` scores a candidate on whether its fact belongs in a doc, so a worthless comment drops out of its proposal list instead of being deleted from the code.
- **Brief:** load `vet-fact` and `tighten-instruction` via the Skill tool and relay their criteria text — subagents don't inherit a parent-loaded skill.
- **Return:** `{ files_changed: [paths], corrected: N, deleted: N, tightened: N, doc_candidates: [{ file, fact }] | null }` — merging shards: join their `doc_candidates` lists, de-duplicate `files_changed`.
