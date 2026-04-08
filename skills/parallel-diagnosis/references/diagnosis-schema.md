# Diagnosis Schema v1

The canonical schema for structured diagnosis output. Used by parallel-diagnosis.

## DiagnosisOutput

```
DiagnosisOutput {
  schema_version: string, always "v1",
  status: "diagnosed" | "not_a_bug" | "inconclusive",
  root_cause: string, unified root cause (1-3 sentences),
  confidence: "high" | "medium" | "low",
  affected_files: string[], file paths involved in the root cause,
  fix_direction: string, what should be fixed and how, in prose — NOT code,
  agreement: "converged" | "resolved" | "escalated",
  agent_reports: AgentReport[]
}
```

## AgentReport

```
AgentReport {
  agent_id: number, 1 | 2,
  root_cause: string, this agent's root cause assessment,
  affected_files: string[], file paths this agent identified,
  fix_direction: string, this agent's proposed fix direction,
  confidence_notes: string, any caveats or uncertainties this agent noted
}
```

## Field notes

- `status` — `"diagnosed"`: normal case, root cause found and actionable. `"not_a_bug"`: both agents concluded the reported behavior is not a bug — terminal, no downstream skills needed. `"inconclusive"`: couldn't determine root cause, escalated to human for further investigation.
- `confidence` — `"high"`: both agents agreed on root cause. `"medium"`: orchestrator resolved a disagreement. `"low"`: significant uncertainty remains (e.g., one agent failed, or orchestrator resolution was shaky).
- `agreement` — `"converged"`: agents independently reached the same conclusion. `"resolved"`: agents disagreed but the orchestrator reconciled. `"escalated"`: human input was needed to resolve.
- `root_cause` — the unified assessment, not a copy of either agent's report. When agents disagreed and the orchestrator resolved, this reflects the orchestrator's judgment.
- `fix_direction` — prose description of what to change and where. Enough detail for fix-loop or a human to act on, but no code.
- `affected_files` — union of files from both agents, filtered to those relevant to the unified root cause.
- `agent_reports` — both raw reports preserved for transparency. Downstream consumers can trace reasoning back to source.
- `confidence_notes` — per-agent field. Agents should be honest about what they're unsure of. Empty string if no caveats.
