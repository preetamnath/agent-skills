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

These skills follow an **open standard** so they can work with any AI coding agent (like Gemini CLI, Claude Code, Cursor, or OpenCode). 

You can install them globally to use them in every project, or locally for just one project.

### 1. Global Installation (Recommended)
This makes your skills available everywhere on your computer.

```bash
# Create the standard skills folder
mkdir -p ~/.agents/skills

# Copy the skills into it
cp -r skills/* ~/.agents/skills/
```

**For Claude Code users:**  
Claude looks in a different folder. You can link the folders so your skills work in both tools:
```bash
mkdir -p ~/.claude/skills
ln -s ~/.agents/skills/* ~/.claude/skills/
```

### 2. Local Installation
If you only want these skills available in a specific project, copy them into that project's folder.

```bash
# For most agents (Gemini CLI, etc.)
mkdir -p .agent/skills
cp -r /path/to/agent-skills/skills/* .agent/skills/

# For Claude Code
mkdir -p .claude/skills
cp -r /path/to/agent-skills/skills/* .claude/skills/
```

## Usage

Once installed, Gemini CLI will automatically detect and use these skills when relevant to your tasks.

## License

[MIT](LICENSE.md)
