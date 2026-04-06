---
name: polaris-web-components
description: "Polaris web component catalog and rules for the polaris-app-home surface. Use when building UI with <s-*> components, looking up props/attributes, composing layouts, or validating markup. Not for backend code or checkout extensions."
model: opus
---

# Polaris Web Components

This skill provides the component catalog, rules, and patterns for `polaris-app-home`. All MCP tool calls (doc search, validation) route through the `/shopify-dev-mcp` skill.

## Workflow

1. **Check the catalog** — Read `references/app-home-index.md` (relative to this skill directory) for the component catalog, App Bridge APIs, and layout compositions — covers available components, props/attributes, and compositions.
2. **Need more detail?** — Invoke `/shopify-dev-mcp` to search docs (`search_docs_chunks` with `api_name: "polaris-app-home"`). **Do NOT use `fetch_full_docs`** — it is deprecated for this surface.
3. **Generate code** — follow the rules below.
4. **Validate** — Invoke `/shopify-dev-mcp` to validate generated markup (`validate_component_codeblocks`).
5. **Fix & re-validate** — if validation fails, fix and re-validate via `/shopify-dev-mcp`.

For components NOT listed in the catalog, invoke `/shopify-dev-mcp` to discover them. This skill covers `polaris-app-home` only. For checkout extension components, route entirely through `/shopify-dev-mcp`.


## Rules

- **Never use deprecated components** — use the recommended replacement.
- **`<s-link>` is for navigation only** — Never use `<s-link>` for actions. Use `<s-button>` or `<s-clickable>` instead.
- **`showOverlay()` / `hideOverlay()` are DOM methods, not App Bridge** — Call these on `<s-modal>` and `<s-popover>` element refs directly (e.g., `document.getElementById('my-modal')?.showOverlay()`). They are NOT `shopify.*` APIs.
- **SpacingKeyword / SizeKeyword scale** — Numbers increase with size: `small-500` (smallest) → `small-400` → `small-300` → `small-200` → `small-100` → `small` → `base` → `large` → `large-100` → `large-200` → `large-300` → `large-400` → `large-500` (largest). Used by `gap`, `padding`, `border` size, etc. `none` is also valid for spacing/padding.


## Common Patterns

Copy-paste friendly patterns from this codebase.

### Icon-only button
Tertiary button with just an icon — used for delete, edit, collapse, etc.
```jsx
<s-button variant="tertiary" tone="critical" icon="delete" accessibilityLabel="Remove item" onClick={handleRemove} />
```

### Collapsible box
Toggle content visibility without unmounting. Uses `<s-box display>` with the `undefined` omission pattern.
```jsx
<s-box display={expanded ? undefined : 'none'}>
  {/* content stays mounted, just hidden */}
</s-box>
```

### Inline divider with label
Horizontal rule with a centered text label (AND/OR separators). Requires `style={{ flex: 1 }}` on dividers — no native prop for this.
```jsx
<div style={{ display: 'flex', alignItems: 'center', gap: 'var(--p-space-300, 12px)' }}>
  <s-divider style={{ flex: 1 }} />
  <s-text color="subdued" type="strong">OR</s-text>
  <s-divider style={{ flex: 1 }} />
</div>
```
