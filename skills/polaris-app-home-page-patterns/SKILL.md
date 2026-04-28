---
name: polaris-app-home-page-patterns
description: "Polaris App Home page templates (Homepage, Index, Details, Settings) and compositions (Empty state, Setup guide, Callout card, etc.) — index of named patterns to look up via shopify-dev-mcp. TRIGGER when: scaffolding an App Home page or using a named composition (Empty state, Setup guide, Callout card, etc.)."
model: opus
---

# Polaris App Home — Page Patterns

Index of Shopify-documented templates (full-page layouts) and compositions (multi-component recipes built from `<s-*>` web components) on the Polaris App Home surface. Each entry below carries the structural skeleton, intent, and anti-patterns so the agent can scaffold without a fetch round-trip; consult `shopify-dev-mcp` only for full canonical examples or details beyond the skeleton.

## When to use

YES: Scaffolding a new full page in an Admin App Home app (Homepage, Index, Details, Settings).
YES: A task names or implies a known composition pattern (Empty state, Setup guide, Callout card, Metrics card, Resource list, etc.).
NO: Component-level work — use `polaris-app-home-web-components`.
NO: API-level work (toast, modal, save bar) — use `polaris-app-home-app-bridge`.

## Instructions

1. Match the task to a [Template](#templates) or [Composition](#compositions) below; use the listed skeleton as a starting point.
2. For canonical detail beyond the skeleton, route through `shopify-dev-mcp` → `search_docs_chunks` with `api_name: "polaris-app-home"` and the pattern name as the prompt (e.g., `"Settings template"`, `"Setup guide composition"`).
3. Implement using the Polaris components from `polaris-app-home-web-components` and APIs from `polaris-app-home-app-bridge`. Combine with the [Common Composition Idioms](#common-composition-idioms) for cross-pattern building blocks.
<!-- Validation flow mirrors agents/shopify-polaris-app-home-developer.md — sync core protocol when that changes. -->
4. Validate the resulting markup via `shopify-dev-mcp` → `validate_component_codeblocks` with `api: "polaris-app-home"`. If validation fails twice on the same artifact, stop and surface the error via the `AskUserQuestion` tool with options: "Retry with hints", "Skip validation", "Abort". Recommended: "Retry with hints".

## Rules

- **Patterns are reference examples, not strict templates.** Use the skeleton as a starting point and adapt freely with `<s-*>` components from `polaris-app-home-web-components`. For canonical implementation detail, retrieve via `search_docs_chunks` rather than inventing from memory.
- **Match Shopify's route conventions for templates.** Homepage → `app._index.jsx`. Index → `app.[resources].jsx` (plural noun). Details → `app.[resource].$id.jsx` (singular noun + id segment). Settings → `app.settings.jsx`.
- **Honour stated anti-patterns.** Each entry's `Avoid:` line reflects an explicit warning in Shopify's docs. Treat these as constraints, not suggestions.

---

## Templates

Full-page layouts. One template per page route.

### Homepage —
Composes: single optional `<s-banner>`, Setup guide, Metrics card grid, Callout card, Media card or featured-app grid, Footer help.
Route: `app._index.jsx`.
Doc: https://shopify.dev/docs/api/app-home/patterns/templates/homepage

### Index —
Composes: Index table (primary content), Empty state (when no resources), optional filter chips above the table, Footer help.
Route: `app.[resources].jsx` (plural noun).
Doc: no standalone template page in Shopify's docs — derive structure from the [Index table](#index-table--) composition skeleton wrapped in `<s-page>`.

### Details —
Skeleton: `<form><s-page><s-section>* (main fields) + <s-box slot="aside">…</s-box></s-page></form>`.
Composes: editable field stack, optional inline `<s-table>` (paginated if >10 rows), sidebar (status/metadata/summary), App Bridge Save Bar, confirmation `<s-modal>` for destructive actions.
Route: `app.[resource].$id.jsx` (singular noun + id).
Doc: https://shopify.dev/docs/api/app-home/patterns/templates/details

### Settings —
Skeleton: `<form data-save-bar><s-page><s-section>* (logical groups of form controls)</s-page></form>`.
Composes: grouped form `<s-section>`s (Store info, Notifications, Preferences), Connected accounts (Account connection grid), Interstitial nav rows linking to sub-pages, destructive Tools section, Footer help.
Route: `app.settings.jsx`.
Doc: https://shopify.dev/docs/api/app-home/patterns/templates/settings

## Compositions

Reusable blocks. Combine inside templates or other pages.

### Account connection —
Skeleton: `<s-section><s-stack><s-grid>` with `<s-grid-item>` per service (each holding `<s-stack>` + `<s-button>`); status `<s-text>`; disconnect `<s-modal>`; outcome `<s-banner>` or toast.
Doc: https://shopify.dev/docs/api/app-home/patterns/compositions/account-connection

### App card —
Skeleton: `<s-clickable><s-grid><s-thumbnail/> + <s-box>` (name + description) + `<s-stack><s-button/></s-stack></s-grid></s-clickable>`.
Doc: https://shopify.dev/docs/api/app-home/patterns/compositions/app-card

### Callout card —
Skeleton: `<s-section><s-grid><s-grid>` (heading + paragraph + `<s-stack>` of buttons) + tertiary `<s-button icon="x">` (dismiss)`</s-grid></s-section>`.
Avoid: routine updates or non-critical info; use sparingly and remove once the merchant engages.
Doc: https://shopify.dev/docs/api/app-home/patterns/compositions/callout-card

### Empty state —
Skeleton: `<s-section><s-grid><s-box><s-image/></s-box> + <s-grid><s-stack><s-heading/><s-paragraph/></s-stack> + <s-button-group><s-button/></s-button-group></s-grid></s-grid></s-section>`.
Doc: https://shopify.dev/docs/api/app-home/patterns/compositions/empty-state

### Footer help —
Skeleton: `<s-stack><s-text><s-link/></s-text></s-stack>`.
Doc: https://shopify.dev/docs/api/app-home/patterns/compositions/footer-help

### Index table —
Skeleton: `<s-section><s-table><s-grid slot="filters">` (search + sort) + `<s-table-header-row/> + <s-table-body><s-table-row><s-table-cell/>×N></s-table-body></s-table></s-section>`.
Avoid: small datasets that don't benefit from search/filter (drop to Resource list); permanently visible row actions (reveal on hover); skipping pagination on large datasets.
Doc: https://shopify.dev/docs/api/app-home/patterns/compositions/index-table

### Interstitial nav —
Skeleton: `<s-section><s-box>` repeating `<s-clickable><s-grid>` (label `<s-box>` + trailing `<s-icon/>`)`</s-grid></s-clickable> + <s-divider/>`.
Doc: https://shopify.dev/docs/api/app-home/patterns/compositions/interstitial-nav

### Media card —
Skeleton: `<s-box><s-clickable><s-image/></s-clickable> + <s-divider/> + <s-grid>` (`<s-heading/>` + `<s-button/>`)`</s-grid></s-box>`.
Avoid: omitting `accessibilityLabel` on the interactive image/clickable.
Doc: https://shopify.dev/docs/api/app-home/patterns/compositions/media-card

### Metrics card —
Skeleton: `<s-section><s-grid>` repeating `<s-clickable><s-grid> + <s-stack> + <s-badge/>` (trend)`</s-clickable> + <s-divider/></s-grid></s-section>`.
Doc: https://shopify.dev/docs/api/app-home/patterns/compositions/metrics-card

### Resource list —
Skeleton: `<s-section><s-stack><s-grid>` (controls/filters) + `<s-stack>` (items each wrapped in `<s-clickable>`)`</s-stack></s-section>`.
Avoid: very large or paginated datasets — escalate to Index table.
Doc: https://shopify.dev/docs/api/app-home/patterns/compositions/resource-list

### Setup guide —
Skeleton: `<s-section><s-grid>` (header + progress) + `<s-box>` repeating `<s-box><s-grid>` (checkbox + toggle)`</s-grid> + <s-box>` (collapsible details)`</s-box></s-section>`.
Avoid: not persisting dismissal across sessions — back it with `localStorage` or a DB row so the guide doesn't reappear.
Doc: https://shopify.dev/docs/api/app-home/patterns/compositions/setup-guide

## Common Composition Idioms

Cross-pattern building blocks that recur across the catalog above. Reach for these when assembling or adapting a pattern.

1. **Header row with dismiss + toggle.** `<s-grid gridTemplateColumns="1fr auto auto" alignItems="center">` containing `<s-heading>` + tertiary `<s-button icon="x">` + tertiary `<s-button icon="chevron-up">`. Used by Setup guide, Callout card.
2. **Card container.** `<s-box border="base" background="base" borderRadius="base" overflow="hidden">`. Wraps Media card, App card, Metrics card cells.
3. **Image-with-text layout.** `<s-grid gridTemplateColumns="1fr auto" gap="base" alignItems="center">` with text grid on left, `<s-image>` constrained to ~80px on right. Used by App card, Setup guide step rows.
4. **Action bar.** `<s-stack direction="inline" gap="small-200">` with primary `<s-button>` + tertiary-neutral `<s-button>`. Used in Empty state, Callout card, Details template footer.
5. **Centered illustration block.** `<s-grid justifyItems="center" maxInlineSize="450px" gap="base">` wrapping image + heading + paragraph + button-group. Empty state's anchor layout.
6. **Save-bar form wrapper.** `<form data-save-bar>` around `<s-page>` for any page with editable fields — Settings and Details rely on this for App Bridge unsaved-change protection.
7. **Slotted controls.** `slot="filters"` on a `<s-grid>` inside `<s-table>` (search/sort), `slot="aside"` on `<s-box>` inside `<s-page>` (Details sidebar). Use named slots instead of inventing layout containers.
