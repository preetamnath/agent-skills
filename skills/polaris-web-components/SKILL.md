---
name: polaris-web-components
description: "Polaris web component catalog and rules for the polaris-app-home surface. Use when building UI with <s-*> components, looking up props/attributes, composing layouts, or validating markup. Not for backend code or checkout extensions."
model: opus
---

# Polaris Web Components

Component catalog, rules, and patterns for `polaris-app-home`. MCP tool calls (doc search, validation) route through `/shopify-dev-mcp`.

## When to use

Building UI with `<s-*>` components, looking up props/attributes, composing layouts, or validating markup for `polaris-app-home`.
Not for backend code or checkout extensions — route those through `/shopify-dev-mcp`.

## Instructions

### 1 — Check the catalog

Consult the [Component Catalog](#component-catalog) below for available components, props/attributes, App Bridge APIs, and layout compositions.

### 2 — Search docs if needed

Invoke `/shopify-dev-mcp` to search docs (`search_docs_chunks` with `api_name: "polaris-app-home"`). **Do NOT use `fetch_full_docs`** — it is deprecated for this surface.

### 3 — Generate code

Follow the rules below.

### 4 — Validate

Invoke `/shopify-dev-mcp` to validate generated markup (`validate_component_codeblocks`).

### 5 — Fix and re-validate

If validation fails, fix and re-validate via `/shopify-dev-mcp`.

For components NOT listed in the catalog, invoke `/shopify-dev-mcp` to discover them. For checkout extension components, route entirely through `/shopify-dev-mcp`.

## Rules

- **Never use deprecated components.** Use the recommended replacement.
- **`<s-link>` is for navigation only.** Never use `<s-link>` for actions. Use `<s-button>` or `<s-clickable>` instead.
- **`showOverlay()` / `hideOverlay()` are DOM methods, not App Bridge.** Call these on `<s-modal>` and `<s-popover>` element refs directly (e.g., `document.getElementById('my-modal')?.showOverlay()`). They are NOT `shopify.*` APIs.
- **SpacingKeyword / SizeKeyword scale.** Numbers increase with size: `small-500` (smallest) → `small-400` → `small-300` → `small-200` → `small-100` → `small` → `base` → `large` → `large-100` → `large-200` → `large-300` → `large-400` → `large-500` (largest). Used by `gap`, `padding`, `border` size, etc. `none` is also valid for spacing/padding.

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

---

<!-- source: references/polaris-app-home-catalog.md -->

## Component Catalog

### Layout & Structure

| Element | Purpose | Key Props / Gotchas |
|---------|---------|---------------------|
| `<s-app>` | Root app wrapper | Must be outermost `<s-*>` element. One per app. |
| `<s-page>` | Page container | `heading` (NOT `title`). Slots: `primary-action`, `secondary-actions`, `aside`, `breadcrumb-actions`, `accessory`. `inline-size`: `small`/`base`/`large`. |
| `<s-section>` | Content card/group | `heading` attr. `padding`: `base` (default) / `none` (full-bleed for tables). `accessibilityLabel` for headingless sections. `slot="aside"` on page for sidebar. **Only slot is `children` — no `description` or other named slots.** **Top-level sections = cards; nested sections = plain.** |
| `<s-stack>` | Flex layout | `direction`: `inline` (row) / `block` (column, default). `gap` (SpacingKeyword — **no default, always set explicitly**). `alignItems`, `alignContent`, `justifyContent`. Has all Box props. **Implicit flex-wrap — no `wrap` prop.** |
| `<s-grid>` | CSS grid layout | `gridTemplateColumns` (**NOT `columns`**) — CSS track values: `"1fr auto"`, `"repeat(3, 1fr)"`. `gridTemplateRows` — same syntax. `gap` / `columnGap` / `rowGap` (SpacingKeyword). `alignItems`, `justifyContent`, `alignContent`, `justifyItems`. Has all Box props. Child `<s-grid-item>` uses `gridColumn` / `gridRow` (e.g. `gridColumn="span 2"`). |
| `<s-grid-item>` | Child of `<s-grid>` | `gridColumn`, `gridRow` for placement. |
| `<s-box>` | Passive container | `padding` / `paddingBlock` / `paddingInline` (PaddingKeyword: `none` / `small-100`..`large-500` / `base`). `background` (BackgroundColorKeyword: `transparent` / `subdued` / `base` / `strong`). `border`: `"size"` or `"size color"` or `"size color style"` (e.g. `border="base subdued dashed"`). `borderRadius` (`none` / `small` / `small-100` / `small-200` / `base` / `large` / `large-100` / `large-200`). `display` (`auto` / `none`) for collapsible patterns. `overflow` (`visible` / `hidden`). `inlineSize` / `blockSize` / `maxInlineSize` / `minInlineSize` (SizeUnits or `auto`). **No flex/grid layout props.** |
| `<s-divider>` | Visual separator | `direction="inline"` = horizontal (default). `direction="block"` = vertical. |
| `<s-app-nav>` | Sidebar navigation | Uses `<s-link>` children. Example: `<s-app-nav><s-link href="/funnels" rel="home">Home</s-link></s-app-nav>`. |
| `<s-query-container>` | CSS container query context | `containerName` attr. Establishes a `@container` context for responsive child layouts. |

### Typography & Content

| Element | Purpose | Key Props / Gotchas |
|---------|---------|---------------------|
| `<s-heading>` | Section heading | Auto-levels based on nesting inside `<s-section>`. |
| `<s-text>` | Inline styled text | `type`: `generic` / `strong` / `address` / `redundant`. **No `fontWeight` attribute — use `type="strong"` for bold, full stop.** `color`: `base` / `subdued`. `tone`: `auto` / `neutral` / `info` / `success` / `warning` / `critical` / `caution`. Renders inline — wrap in `<s-paragraph>` or `<s-stack>` to stack vertically. |
| `<s-paragraph>` | Block text | `tone`, `color="subdued"`. Contains inline elements like `<s-text>`, `<s-link>`. |
| `<s-chip>` | Static display tag | `color` (`base`/`subdued`/`strong`). Non-interactive. |
| `<s-tooltip>` | Hover/focus hint | `id` required + `interest-for` on trigger element (NOT `command-for`). |
| `<s-ordered-list>` | Numbered list | Contains `<s-list-item>` children. |
| `<s-unordered-list>` | Bulleted list | Contains `<s-list-item>` children. |
| `<s-list-item>` | List item | Child of `<s-ordered-list>` or `<s-unordered-list>`. |

### Actions

| Element | Purpose | Key Props / Gotchas |
|---------|---------|---------------------|
| `<s-button>` | Actions, form submit, links | `variant` for styling (`primary`/`secondary`/`tertiary`), NOT `type`. `type` is form behavior (`submit`/`button`/`reset`). `icon` for leading icon (icon-only: omit text content, add `accessibilityLabel`). `tone`: `auto`/`critical`. `command-for` + `command` to trigger overlays. |
| `<s-link>` | Text links | **Triggers navigation** — use intentionally for page transitions. For sidebar navigation, use inside `<s-app-nav>`. For in-page links, be aware it triggers navigation — use for intentional page transitions only. |
| `<s-clickable>` | Generic clickable area | Renders `<a>` with `href`/`target`/`download`, `<button>` without. Full box-model props like `<s-box>`: `border`, `borderRadius`, `background`, `padding`, `display`, `inlineSize`, `overflow`. `loading` boolean. `commandFor` + `command` to trigger overlays. `disabled` boolean. Use for custom interactive cards/regions when `<s-button>` or `<s-link>` don't fit. |
| `<s-menu>` | Action list dropdown | Needs `id` + `command-for` on trigger button. Accepts `<s-button>` and `<s-section>` children. |
| `<s-clickable-chip>` | Interactive filter/tag chip | `removable` for dismiss; `color` (`base`/`subdued`/`strong`); `command-for` supported. |
| `<s-button-group>` | Grouped buttons in structured layout | `gap`: `base`/`none` only (NOT full SpacingKeyword). Slots: `primary-action`, `secondary-actions`, `children`. |

### Forms

| Element | Purpose | Key Props / Gotchas |
|---------|---------|---------------------|
| `<s-text-field>` | Single-line text input | `icon` for leading icon. `accessory` slot for trailing content. `prefix`/`suffix` string attrs for inline text. `details` for helper text below field. `labelAccessibilityVisibility="exclusive"` to visually hide label. `onInput` fires every keystroke; `onChange` fires on blur/Enter. |
| `<s-text-area>` | Multi-line text input | `rows`, `max-length`. `onInput` fires every keystroke; `onChange` fires on blur/Enter. |
| `<s-checkbox>` | Single boolean toggle | `label` required. `value` attr for form data. |
| `<s-choice-list>` | Radio/checkbox group | Contains `<s-choice>` children. `multiple` for checkboxes, omit for radios. `label` (field label). `values` (array of selected values). `details` for helper text. `onChange` returns `e.target.values` (string array). |
| `<s-choice>` | Individual option in choice-list | `value` + `selected` attrs. `defaultSelected` for uncontrolled default. `accessibilityLabel` replaces visible label for screen readers. Slots: `details` (subtitle below label), `secondary-content` (rich content — text fields, buttons, etc. below the choice). |
| `<s-number-field>` | Numeric input | `label`, `min`, `max`, `step`, `value`, `inputMode` (`numeric`/`decimal`). `prefix`/`suffix` for inline text (e.g. `$`). `details` for helper text. `onInput` fires every keystroke; `onChange` fires on blur/Enter. |
| `<s-select>` | Dropdown select | Contains `<s-option>` children. `placeholder` for default text. |
| `<s-switch>` | Toggle switch | `label` + `checked` boolean. `details` for helper text. `error`, `disabled`, `required`. `defaultChecked` for uncontrolled. |
| `<s-drop-zone>` | File upload area | `accept` for file types, `multiple` for multi-file. |
| `<s-date-field>` | Date text input | `allow` restricts date range (e.g., `"2025--"`). |
| `<s-option-group>` | Grouped options in select | Groups `<s-option>` children. |
| `<s-option>` | Individual option in select | `value` attr. |
| `<s-url-field>` | URL input | `label`, `placeholder`, `autocomplete="url"`. Built-in URL validation. |
| `<s-email-field>` | Email input | `label`, `placeholder`, `autocomplete="email"`. Built-in email validation. |
| `<s-money-field>` | Currency input | `label`, `min`, `max`. Built-in currency formatting. |
| `<s-password-field>` | Password input | `label`, `autocomplete`, `minLength`. Built-in masking. |
| `<s-search-field>` | Search input | `label`, `placeholder`. `labelAccessibilityVisibility="exclusive"` common. |
| `<s-color-field>` | Color input with picker | `label`, `value` (hex), `alpha` boolean. |
| `<s-color-picker>` | Visual color palette | `value` (hex), `alpha` boolean. |
| `<s-date-picker>` | Calendar date picker | `type` (`single`/`range`), `value`, `name`. |

### Feedback & Status

| Element | Purpose | Key Props / Gotchas |
|---------|---------|---------------------|
| `<s-banner>` | Prominent message/alert | `heading` (NOT `title`). `tone` (`info`/`success`/`warning`/`critical`). `dismissible` boolean. Slot `secondary-actions` for buttons (max 2). `hidden` to control visibility. |
| `<s-badge>` | Status label/tag | `tone`: `success`/`warning`/`critical`/`info`/`neutral`/`caution`. `color`: `base`/`subdued`/`strong`. `icon` attr. |
| `<s-spinner>` | Loading indicator | `size`: `base`/`large`/`large-100` (NO `small`). `accessibility-label` required. |

> **`<s-skeleton-body-text>` does NOT exist as a web component. Never generate it. Use `<s-spinner>` for loading states.**

### Media & Visuals

| Element | Purpose | Key Props / Gotchas |
|---------|---------|---------------------|
| `<s-icon>` | Graphic symbol | `type` (icon name: `"cart"`, `"delete"`, `"check-circle"`, `"product"`, `"collection"`, etc.). `tone`: `auto`/`neutral`/`info`/`success`/`warning`/`critical`. `color`: `base`/`subdued`. `size`: `small`/`base` only (**no `large`**). `interestFor` to link to a `<s-tooltip>` by id. |
| `<s-image>` | Responsive image | `aspect-ratio`, `object-fit`, `loading="lazy"` attrs. |
| `<s-thumbnail>` | Small preview image | `src`, `alt`. Sizes: `small`/`small-200`/`small-100`/`base`/`large`/`large-100`. |
| `<s-avatar>` | User/entity avatar | `initials`, `src`, `alt`. Sizes: `small`/`small-200`/`base`/`large`/`large-200`. |

### Embedded Surfaces

| Element | Purpose | Key Props / Gotchas |
|---------|---------|---------------------|
| `<s-app-window>` | Embedded app iframe | `id` required. `src` for iframe URL (required). Imperative API via ref: `.show()` / `.hide()` / `.toggle()`. Fires both `show` and `hide` events. Used for live previews (e.g., offer preview in OfferStep). |

### Overlays

| Element | Purpose | Key Props / Gotchas |
|---------|---------|---------------------|
| `<s-popover>` | Contextual overlay | `id` required + `command-for` on trigger button. `inline-size` for width (e.g., `"300px"`). Also `block-size`, `max-inline-size`, `max-block-size`. **No `heading` prop** (unlike `<s-modal>`). |
| `<s-modal>` | Dialog overlay | `heading` (NOT `title`). `id` required + `command-for` on trigger button. Slots: `primary-action`, `secondary-actions`. `size`: `small`/`small-100`/`base`/`large`/`large-100`. `padding="none"` for full-bleed content. `command="--hide"` on inner buttons to close. |

### Table

| Element | Purpose | Key Props / Gotchas |
|---------|---------|---------------------|
| `<s-table>` | Data table container | `variant="auto"` for responsive. Wrap in `<s-section padding="none">` for full-width. `paginate`/`hasNextPage`/`hasPreviousPage` props. Events: `nextpage`/`previouspage`. `filters` slot for table filters. |
| `<s-table-header-row>` | Header row wrapper | Contains `<s-table-header>` children. |
| `<s-table-header>` | Column header | `list-slot` (`primary`/`labeled`/`inline`/`secondary`) controls responsive behavior. `format="numeric"` or `"currency"` for alignment. |
| `<s-table-body>` | Table body wrapper | Contains `<s-table-row>` children. |
| `<s-table-row>` | Table data row | Contains `<s-table-cell>` children. |
| `<s-table-cell>` | Table data cell | |

## App Bridge APIs

| API | Purpose | Usage |
|-----|---------|-------|
| Toast | Transient messages | `shopify.toast.show('Saved')` |
| Modal API | Programmatic overlay control | DOM methods on `<s-modal>` / `<s-popover>` elements: `el.showOverlay()` / `el.hideOverlay()` |
| Save Bar | Unsaved form changes bar | `data-save-bar` on form + `<ui-save-bar>` |
| Resource Picker | Product/collection picker | `shopify.resourcePicker()` |
| Navigation | URL management | Managed via `<s-app-nav>` + App Bridge |
| Loading | Global loading bar | Title bar loading indicator |
| ID Token | Session token for API calls | `shopify.idToken()` |
| App Window | Programmatic app window control | `shopify.appWindow.hide()` — bridge API separate from `<s-app-window>` element |

## Compositions & Templates

Ready-made patterns combining web components and APIs. Use `search_docs_chunks` with `api_name: "polaris-app-home"` and the pattern name to get implementation code.

### Templates (full-page layouts)

| Template | Purpose |
|----------|---------|
| Homepage | Primary landing page — key info and actions at a glance |
| Details | Edit/view individual resources in dual-column layout |
| Index | List page with search, filters, sorting, bulk actions |
| Settings | App configuration with sectioned forms |

### Compositions (reusable blocks)

| Composition | Purpose |
|-------------|---------|
| Account connection | Connect/disconnect external accounts |
| App card | Promote related apps within your app |
| Callout card | Encourage action on features/opportunities — **single CTA with illustration** |
| Empty state | Guidance when no data exists |
| Footer help | Link to docs/support at page bottom |
| Index table | Data table with search, filter, sort, bulk actions — **for large datasets** |
| Interstitial nav | Deeper navigation linking to related pages |
| Media card | Visual content with actionable info — **image/video alongside text** |
| Metrics card | Key stats and trends at a glance |
| Resource list | Collection of same-type objects — **simpler than index table, no bulk actions** |
| Setup guide | Onboarding checklist with progress tracking |
