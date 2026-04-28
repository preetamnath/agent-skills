---
name: polaris-app-home-web-components
description: "Polaris `<s-*>` web component catalog for the Admin App Home surface. Use when writing/editing Polaris markup — `<s-page>`, `<s-section>`, `<s-button>`, `<s-modal>`, tables, forms, layout. TRIGGER when: code contains `<s-*>` tags; user asks to build/update Admin App Home UI."
model: opus
---

# Polaris App Home Web Components

Component catalog, rules, and patterns for the Polaris `<s-*>` web components on the `polaris-app-home` surface. Title bar configuration is via `<s-page>` slots — covered in the Layout & Structure catalog.

## When to use

YES: Writing or editing `<s-*>` markup for an Admin App Home page (the Shopify-hosted iframe SPA).
NO: Building post-purchase or other extensions — use `post-purchase-extension` and other extension skills.
NO: Calling `shopify.*` APIs, `useAppBridge`, or using `<s-app-nav>` / `<s-app-window>` / save bar — use `polaris-app-home-app-bridge`.
NO: Scaffolding a Homepage / Index / Details / Settings page or a named composition (Empty state, Setup guide, etc.) — use `polaris-app-home-page-patterns` first.

## Instructions

1. Find the component in the [Component Catalog](#component-catalog). If missing, route through `shopify-dev-mcp` → `search_docs_chunks` with `api_name: "polaris-app-home"`. Do NOT use `fetch_full_docs` for this surface.
2. Write markup following the [Rules](#rules) and [Common Idioms](#common-idioms).
<!-- Validation flow mirrors agents/shopify-polaris-app-home-developer.md — sync core protocol when that changes. -->
3. Validate via `shopify-dev-mcp` → `validate_component_codeblocks` with `api: "polaris-app-home"`. If validation fails twice on the same artifact, stop and surface the error via the `AskUserQuestion` tool with options: "Retry with hints", "Skip validation", "Abort". Recommended: "Retry with hints".

## Rules

- **No `<s-app>` element.** It does not exist as a Polaris component. `<s-page>` is the standard outer wrapper.
- **`<s-skeleton-body-text>` does NOT exist.** Use `<s-spinner>` for loading states. For button loading, use the `loading` prop on `<s-button>`.
- **`<s-link>` is for navigation only.** Triggers page transitions. Never use it for actions — use `<s-button>` or `<s-clickable>` instead.
- **Title bar = `<s-page>` slots.** There is no `<s-title-bar>` component. Set `heading` on `<s-page>` and use the `primary-action`, `secondary-actions`, `breadcrumb-actions`, `accessory` slots for title-bar content.
- **Save bar = `<form data-save-bar>`.** There is no `<s-save-bar>` component. The form attribute + `shopify.saveBar.*` API live in `polaris-app-home-app-bridge`.
- **App Bridge components live in another skill.** `<s-app-nav>` and `<s-app-window>` are App Bridge web components — they don't validate as JSX in `validate_component_codeblocks`. See `polaris-app-home-app-bridge`.
- **`showOverlay()` / `hideOverlay()` / `toggleOverlay()` are DOM instance methods on `<s-modal>` and `<s-popover>` element refs.** Namespaced equivalents `shopify.modal.show(id)` / `hide(id)` / `toggle(id)` also exist (covered in `polaris-app-home-app-bridge`).
- **SpacingKeyword / SizeKeyword scale (smallest to largest):** `small-500` → `small-400` → `small-300` → `small-200` → `small-100` → `small` → `base` → `large` → `large-100` → `large-200` → `large-300` → `large-400` → `large-500`. **Note:** on the `small-N` side, larger N = smaller; on the `large-N` side, larger N = larger. `none` is also valid for spacing/padding.

## Common Idioms

### Icon-only button
Tertiary button with just an icon — used for delete, edit, collapse.
```jsx
<s-button variant="tertiary" tone="critical" icon="delete" accessibilityLabel="Remove item" onClick={handleRemove} />
```

### Collapsible box
Toggle visibility without unmounting. Uses `<s-box display>` with `undefined` omission.
```jsx
<s-box display={expanded ? undefined : 'none'}>
  {/* content stays mounted, just hidden */}
</s-box>
```

### Inline divider with label
Horizontal rule with a centered text label (AND/OR separators). Requires `style={{ flex: 1 }}` on dividers.
```jsx
<div style={{ display: 'flex', alignItems: 'center', gap: 'var(--p-space-300, 12px)' }}>
  <s-divider style={{ flex: 1 }} />
  <s-text color="subdued" type="strong">OR</s-text>
  <s-divider style={{ flex: 1 }} />
</div>
```

---

## Component Catalog

### Layout & Structure

| Element | Purpose | Key Props / Gotchas |
|---------|---------|---------------------|
| `<s-page>` | Page container + admin title bar surface | `heading` (string, NOT `title`). `inline-size`: `small`/`base`/`large`. **Slots configure the admin title bar:** `primary-action` (single `<s-button>`), `secondary-actions` (multiple `<s-button>`s, combine with `<s-menu>` + `command-for` for grouped actions), `breadcrumb-actions` (`<s-link>` back-style), `accessory` (e.g. `<s-badge>` status). Also `aside` slot for sidebar. **No `subtitle` prop** (only on the React `<TitleBar>` wrapper). |
| `<s-section>` | Content card/group | `heading` attr. `padding`: `base` (default) / `none` (full-bleed for tables). `accessibilityLabel` for headingless sections. **Only slot is `children` — no `description` or other named slots.** **Top-level sections = cards; nested sections = plain.** |
| `<s-stack>` | Flex layout | `direction`: `inline` (row) / `block` (column, default). `gap` (SpacingKeyword — **no default, always set explicitly**). `alignItems`, `alignContent`, `justifyContent`. Has all Box props. **Implicit flex-wrap — no `wrap` prop.** |
| `<s-grid>` | CSS grid layout | `gridTemplateColumns` (**NOT `columns`**) — CSS track values: `"1fr auto"`, `"repeat(3, 1fr)"`. `gridTemplateRows` — same syntax. `gap` / `columnGap` / `rowGap` (SpacingKeyword). `alignItems`, `justifyContent`, `alignContent`, `justifyItems`. Has all Box props. |
| `<s-grid-item>` | Child of `<s-grid>` | `gridColumn`, `gridRow` for placement (e.g. `gridColumn="span 2"`). |
| `<s-box>` | Passive container | `padding` / `paddingBlock` / `paddingInline` (PaddingKeyword: `none` / `small-100`..`large-500` / `base`). `background` (`transparent` / `subdued` / `base` / `strong`). `border`: `"size"` / `"size color"` / `"size color style"` (e.g. `border="base subdued dashed"`). `borderRadius` (`none` / `small` / `small-100` / `small-200` / `base` / `large` / `large-100` / `large-200`). `display` (`auto` / `none`). `overflow` (`visible` / `hidden`). `inlineSize` / `blockSize` / `maxInlineSize` / `minInlineSize`. **No flex/grid layout props.** |
| `<s-divider>` | Visual separator | `direction="inline"` (horizontal, default) / `"block"` (vertical). |
| `<s-query-container>` | CSS container query context | `containerName` attr. Establishes a `@container` context for responsive child layouts. |
| `<s-app-window>` | Embedded iframe / secondary window | App Bridge web component, not Polaris — does NOT validate as JSX in `validate_component_codeblocks`. Documented under the App Bridge surface. |

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
| `<s-button>` | Actions, form submit, links | `variant` for styling (`primary`/`secondary`/`tertiary`), NOT `type`. `type` is form behavior (`submit`/`button`/`reset`). `icon` for leading icon (icon-only: omit text content, add `accessibilityLabel`). `tone`: `auto`/`critical`. `command-for` + `command` to trigger overlays. `loading` boolean for in-button loading state (preferred over wrapping a spinner). |
| `<s-link>` | Text links — navigation only | **Triggers page transitions.** Never for actions. Props: `href`, `target`, `download`, `tone`. **`rel="home"` is App Bridge–specific** and fails JSX validation when used inside `<s-app-nav>` — see `polaris-app-home-app-bridge`. |
| `<s-clickable>` | Generic clickable area | Renders `<a>` with `href`/`target`/`download`, `<button>` without. Box-model props like `<s-box>`: `border`, `borderRadius`, `background`, `padding`, `display`, `inlineSize`, `overflow`. `loading`, `disabled` boolean. `commandFor` + `command` to trigger overlays. Use for custom interactive cards/regions when `<s-button>` or `<s-link>` don't fit. |
| `<s-menu>` | Action list dropdown | Needs `id` + `command-for` on trigger button. Accepts `<s-button>` and `<s-section>` children. |
| `<s-clickable-chip>` | Interactive filter/tag chip | `removable` for dismiss; `color` (`base`/`subdued`/`strong`); `command-for` supported. |
| `<s-button-group>` | Grouped buttons in structured layout | `gap`: `base`/`none` only (NOT full SpacingKeyword). Slots: `primary-action`, `secondary-actions`, `children`. |

### Forms

| Element | Purpose | Key Props / Gotchas |
|---------|---------|---------------------|
| `<s-text-field>` | Single-line text input | `icon` for leading icon. `accessory` slot for trailing content. `prefix`/`suffix` string attrs for inline text. `details` for helper text below field. `labelAccessibilityVisibility="exclusive"` to visually hide label. `onInput` fires every keystroke; `onChange` fires on blur/Enter. |
| `<s-text-area>` | Multi-line text input | `rows`, `max-length`. `onInput`/`onChange` semantics same as text-field. |
| `<s-checkbox>` | Single boolean toggle | `label` required. `value` attr for form data. |
| `<s-choice-list>` | Radio/checkbox group | Contains `<s-choice>` children. `multiple` for checkboxes, omit for radios. `label`, `values` (array of selected values), `details`. `onChange` returns `e.target.values` (string array). |
| `<s-choice>` | Individual option in choice-list | `value` + `selected` attrs. `defaultSelected` for uncontrolled. `accessibilityLabel` replaces visible label for SR. Slots: `details` (subtitle), `secondary-content` (rich content below choice). |
| `<s-number-field>` | Numeric input | `label`, `min`, `max`, `step`, `value`, `inputMode` (`numeric`/`decimal`). `prefix`/`suffix` for inline text (e.g. `$`). `details` for helper text. |
| `<s-select>` | Dropdown select | Contains `<s-option>` (and optional `<s-option-group>`) children. `placeholder` for default text. |
| `<s-option-group>` | Grouped options in select | Groups `<s-option>` children. |
| `<s-option>` | Individual option in select | `value` attr. |
| `<s-switch>` | Toggle switch | `label` + `checked` boolean. `details`, `error`, `disabled`, `required`. `defaultChecked` for uncontrolled. |
| `<s-drop-zone>` | File upload area | `accept` for file types, `multiple` for multi-file. |
| `<s-date-field>` | Date text input | `allow` restricts date range (e.g., `"2025--"`). |
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
| `<s-spinner>` | Loading indicator | `size`: `base`/`large`/`large-100` (NO `small`). `accessibility-label` required. **For button loading states, use the `loading` prop on `<s-button>` instead.** |

### Media & Visuals

| Element | Purpose | Key Props / Gotchas |
|---------|---------|---------------------|
| `<s-icon>` | Graphic symbol | `type` (icon name: `"cart"`, `"delete"`, `"check-circle"`, etc.). `tone`: `auto`/`neutral`/`info`/`success`/`warning`/`critical`. `color`: `base`/`subdued`. `size`: `small`/`base` only (**no `large`**). `interestFor` to link to a `<s-tooltip>` by id. |
| `<s-image>` | Responsive image | `aspect-ratio`, `object-fit`, `loading="lazy"` attrs. |
| `<s-thumbnail>` | Small preview image | `src`, `alt`. Sizes: `small`/`small-200`/`small-100`/`base`/`large`/`large-100`. |
| `<s-avatar>` | User/entity avatar | `initials`, `src`, `alt`. Sizes: `small`/`small-200`/`base`/`large`/`large-200`. |

### Overlays

| Element | Purpose | Key Props / Gotchas |
|---------|---------|---------------------|
| `<s-popover>` | Contextual overlay | `id` required + `command-for` on trigger button. `inline-size` for width (e.g., `"300px"`). Also `block-size`, `max-inline-size`, `max-block-size`. **No `heading` prop** (unlike `<s-modal>`). DOM instance methods: `showOverlay()` / `hideOverlay()` / `toggleOverlay()`. |
| `<s-modal>` | Dialog overlay | `heading` (NOT `title`). `id` required + `command-for` on trigger button. Slots: `primary-action`, `secondary-actions`. `size`: `small` / `small-100` / `base` (default) / `large` / `large-100`. `padding="none"` for full-bleed content. `command="--hide"` on inner buttons to close. DOM instance methods: `showOverlay()` / `hideOverlay()` / `toggleOverlay()`. Namespaced equivalents `shopify.modal.show(id)` / `hide(id)` / `toggle(id)` — see `polaris-app-home-app-bridge`. |

### Table

| Element | Purpose | Key Props / Gotchas |
|---------|---------|---------------------|
| `<s-table>` | Data table container | `variant="auto"` for responsive. Wrap in `<s-section padding="none">` for full-width. `paginate` / `hasNextPage` / `hasPreviousPage` props. Events: `nextpage` / `previouspage`. `filters` slot for table filters. |
| `<s-table-header-row>` | Header row wrapper | Contains `<s-table-header>` children. |
| `<s-table-header>` | Column header | `list-slot` (`primary` / `labeled` / `inline` / `secondary`) controls responsive behavior. `format="numeric"` or `"currency"` for alignment. |
| `<s-table-body>` | Table body wrapper | Contains `<s-table-row>` children. |
| `<s-table-row>` | Table data row | Contains `<s-table-cell>` children. |
| `<s-table-cell>` | Table data cell | |
