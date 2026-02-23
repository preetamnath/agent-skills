# Agent Skills

A collection of AI agent skills built for Gemini CLI to help with specialized engineering tasks.

Built by [Preetam Nath](https://github.com/preetamnath).

## Available Skills

| Skill | Description |
|-------|-------------|
| [code-review](skills/code-review/) | Critically analyze code changes for bugs, errors, security holes, and performance issues. |
| [git-commit-message](skills/git-commit-message/) | Generate git commit messages in a specific bullet-point format with a conventional header. |
| [sentry-analysis](skills/sentry-analysis/) | Analyze Sentry error logs, breadcrumbs, and codebase context to diagnose and explain the root cause of issues. |

## Installation

To use these skills with Gemini CLI, copy the desired skill folder(s) to your project's skills directory.

```bash
git clone https://github.com/preetamnath/agent-skills.git
cp -r agent-skills/skills/* /path/to/your/project/
```

## Usage

Once installed, Gemini CLI will automatically detect and use these skills when relevant to your tasks.

## License

[MIT](LICENSE.md)
