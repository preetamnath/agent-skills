# Canonical Agent Delivery

Use this guide after `vet-fact` and `place-fact` establish that repository instructions or project skills must reach more than one agent loader. It owns delivery mechanics, not artifact admission or instruction content.

## Delivery contract

| Surface | Canonical owner | Derived delivery |
|---|---|---|
| Repository instructions | Root or nested `AGENTS.md` | Sibling `CLAUDE.md` as a relative symlink to `AGENTS.md` |
| Project skills | `.agents/skills/<name>/` | Matching `.claude/skills/<name>` delivery, derived by relative symlink |

- Keep one editable path per instruction or skill.
- Use relative links so a clone works at any absolute path.
- Keep `.claude/rules/`, provider commands, and other loader-specific configuration in their native homes; route any shared fact through `place-fact` instead of mirroring whole provider directories.
- Use generated or automatically equality-guarded copies only when a loader cannot follow the required symlink.

## Adopt the contract

1. **Inventory repository-owned surfaces.** Find every root and nested instruction pair and every project skill delivered to more than one loader. Exclude dependencies, generated output, caches, and vendored trees.
2. **Reconcile divergent content.** When editable copies differ, route every surviving fact to one canonical owner before replacing either copy; choose the owner from its delivery contract, not its filename.
3. **Make instructions canonical.** Move the complete current instruction content into `AGENTS.md`, update self-references and headings, then replace the sibling `CLAUDE.md` with the relative link `AGENTS.md`.
4. **Make project skills canonical.** Move the complete skill under `.agents/skills/<name>/`, then derive the matching Claude delivery:
   - A skill containing only `SKILL.md` may use `.claude/skills/<name>/SKILL.md -> ../../../.agents/skills/<name>/SKILL.md`.
   - A skill with scripts, references, or assets must derive every required file. Prefer a whole-directory symlink only after verifying that each supported loader follows directory links; otherwise link each required file or generate and equality-guard the delivery tree.
   - Verify that relative resource paths still resolve from the delivered `SKILL.md`.
5. **Update current references.** Change canonical filenames, same-change rules, tests, and maintained documentation in the same change. Leave dated records historical unless they claim to be current truth.
6. **Verify each loader.** Confirm every supported agent discovers root instructions, nested instructions, skills, and referenced resources at the required trigger.

## Check delivery

Run the shared checker after adding, moving, or removing repository instructions or project skills:

```bash
node /path/to/agent-skills/scripts/validate-agent-delivery.mjs /path/to/repository
```

The repository argument defaults to the current working directory. Use a repository-local guard only when CI must enforce delivery without access to the Agent Skills checkout.

| Surface | Required assertions |
|---|---|
| Instruction delivery | Every discovered instruction directory has a regular `AGENTS.md`; sibling `CLAUDE.md` is a relative symlink whose exact target is `AGENTS.md` and whose resolved path equals the canonical file. |
| Skill delivery | Canonical and delivered skill-name sets match; each `.agents` source is regular; each `.claude` delivery has the expected relative target and resolves to the source; required resources resolve. |
| Copy fallback | A repository-specific check proves generated or unavoidable copies equal their canonical source; the shared checker cannot infer copy relationships. |

Exclude dependency and tool-owned directories explicitly. Run the checker, repository verification, and `git diff --check` before committing.
