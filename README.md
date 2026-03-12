# Agent Skills

A collection of skills for AI coding agents to help with specialized engineering tasks.

Built by [Preetam Nath](https://github.com/preetamnath).

## Available Skills

| Skill | Description |
|-------|-------------|
| [code-review](skills/code-review/) | Critically analyze code changes for bugs, errors, security holes, and performance issues. |
| [git-commit-message](skills/git-commit-message/) | Generate git commit messages in a specific bullet-point format with a conventional header. |
| [adversarial-consensus](skills/adversarial-consensus/) | Multi-agent pattern for producing airtight fixes. Parallel independent diagnosis, consensus synthesis, adversarial critique, then hardened solution. |
| [sentry-analysis](skills/sentry-analysis/) | Analyze Sentry error logs, breadcrumbs, and codebase context to diagnose and explain the root cause of issues. |

## Installation

Install via [skills.sh](https://skills.sh/) — a package manager for AI agent skills. It handles everything: which agents to install for, global vs. per-project, and future updates.

```bash
npx skills add preetamnath/agent-skills
```

During install you'll be prompted to choose which coding agents to install for (Claude Code, Gemini CLI, Cursor, etc.) and whether to install globally or per-project.

### Updating

```bash
npx skills update
```

## Usage

Once installed, your agent will automatically detect and use these skills when relevant to your tasks. You can also invoke them explicitly — for example, in Claude Code, type `/git-commit-message` to generate a commit message.

## License

[MIT](LICENSE.md)
