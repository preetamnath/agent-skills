# Context gauge

How a Claude Code session measures its own context fill in absolute tokens (works because `CLAUDE_CODE_SESSION_ID` is exported to Bash subprocesses):

```bash
python3 -c "
import json, os
sid = os.environ['CLAUDE_CODE_SESSION_ID']
proj = os.path.expanduser('~/.claude/projects/<encoded-project-dir>')
last = None
for line in open(f'{proj}/{sid}.jsonl'):
    try: d = json.loads(line)
    except: continue
    u = (d.get('message') or {}).get('usage')
    if d.get('type') == 'assistant' and u and u.get('input_tokens') is not None: last = u
ctx = last['input_tokens'] + last.get('cache_read_input_tokens',0) + last.get('cache_creation_input_tokens',0)
print(f'{round(ctx/1000)}k')
"
```

`<encoded-project-dir>` is the project path with `/` replaced by `-` (e.g. `-Users-you-code-myrepo`). The transcript JSONL format is internal to Claude Code and can change between releases — if the fields vanish, fall back to the statusline's `context_window` fields and update this recipe plus its consumers.

Consumers (inlined per WRITING-GUIDE's shared schema workflow): `skills/execute-plan/SKILL.md`, `skills/supervise-plan/SKILL.md`.
