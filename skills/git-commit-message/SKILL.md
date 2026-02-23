---
name: git-commit-message
description: Generate git commit messages in a specific bullet-point format with a conventional header.
---

# Git Commit Message Generation

When asked to generate a git commit message, satisfy the following rules:

1. **Gather Context**:
   - Run `git status` to identify all modified, deleted, and untracked (new) files.
   - **Modified files**: Run `git diff <filename>` to see specific changes.
   - **Untracked files**: Run `view_file` to read the full content of new documents.
   - **Deleted files**: Note the removal.
   - **Staged files**: If changes are already staged, run `git diff --cached`.

2. **Draft Message**:
   - Create a conventional commit message based on the *actual* changes found.
   - **Header**: Start with a Conventional Commit header (e.g., `feat:`, `fix:`, `refactor:`) that captures the key change.
   - **Body**: Leave one empty line after the header, then a list of details.
   - **Format**: Use a simple bulleted list (`-`) for the details.
   - **Style**: Use the imperative mood (e.g., "Create", "Update", "Fix", "Refactor").
   - **Quotes**: **NEVER use double quotes (")** in the commit message content. Use single quotes (') instead if you need to quote something.

3. **Execute**:
   - Construct the final command: `git add . && git commit -m "YOUR_MESSAGE_HERE"`.
   - **Output**: Present the final command in a markdown code block (`bash`) so the user can copy/paste if they reject the tool.
   - **Then**, immediately use the `run_command` tool to propose this command.

## Usage Example

**Input**: "Commit these changes."

**Context**: User has modified several files related to the layout.

**Output**:

```bash
git add . && git commit -m "refactor(learn): unify header layout and simplify access logic

- Create learn/layout.tsx shared layout file for learn routes
- Create LearnPagesHeader.tsx to consolidate title/breadcrumb and UserProfileDropDown.tsx across /learn and /learn/:slug routes
- Update code in UnpaidUserBanner.tsx and NoAccessToThisNote.tsx components
- Consolidate 'Paid User' and 'Valid Access Config' checks into unified logic blocks across pages
- Add JSDoc documentation to BreadcrumbLink.tsx, UserProfileDropdown.tsx and learn/layout.tsx"
```

**Action**: Agent then calls `run_command` with the exact string above.
