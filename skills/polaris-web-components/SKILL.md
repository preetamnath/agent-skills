---
name: polaris-web-components
description: "Polaris <s-*> web component catalog, props/slots reference, and layout patterns for the polaris-app-home surface. Use when writing/editing markup with <s-*> tags (<s-page>, <s-section>, <s-stack>, <s-button>, <s-modal>, etc.), building UI in the Admin App Home SPA, looking up a Polaris component's props/slots/tone/size, or calling App Bridge APIs (shopify.toast, shopify.resourcePicker)."
model: opus
---

# Polaris Web Components

Component catalog, rules, and patterns for `polaris-app-home`. MCP tool calls (doc search, validation) route through `/shopify-dev-mcp`.

## Rules

- **Never use deprecated components.** Use the recommended replacement.
- **`<s-link>` is for navigation only.** Never use `<s-link>` for actions. Use `<s-button>` or `<s-clickable>` instead.
- **`showOverlay()` / `hideOverlay()` are DOM methods, not App Bridge.** Call these on `<s-modal>` and `<s-popover>` element refs directly (e.g., `document.getElementById('my-modal')?.showOverlay()`). They are NOT `shopify.*` APIs.
- **SpacingKeyword / SizeKeyword scale.** Numbers increase with size: `small-500` (smallest) → `small-400` → `small-300` → `small-200` → `small-100` → `small` → `base` → `large` → `large-100` → `large-200` → `large-300` → `large-400` → `large-500` (largest). Used by `gap`, `padding`, `border` size, etc. `none` is also valid for spacing/padding.

## Instructions

1. Find component in the [Component Catalog](#component-catalog). If missing, invoke `/shopify-dev-mcp` → `search_docs_chunks` with `api_name: "polaris-app-home"`. Do NOT use `fetch_full_docs` for this surface (deprecated).
2. Write markup following the rules above and [Common Patterns](#common-patterns).
3. Validate via `/shopify-dev-mcp` → `validate_component_codeblocks` with `api: "polaris-app-home"`. If validation fails twice on the same artifact, stop and surface the error to the user.

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

### Actions

| Element | Purpose | Key Props / Gotchas |
|---------|---------|---------------------|
| `<s-button>` | Actions, form submit, links | `variant` for styling (`primary`/`secondary`/`tertiary`), NOT `type`. `type` is form behavior (`submit`/`button`/`reset`). `icon` for leading icon (icon-only: omit text content, add `accessibilityLabel`). `tone`: `auto`/`critical`. `command-for` + `command` to trigger overlays. |
| `<s-link>` | Text links | Navigation only — triggers page transitions. Never for actions (use `<s-button>`/`<s-clickable>`). Inside `<s-app-nav>` for sidebar. |
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
| `<s-url-field>`, `<s-email-field>`, `<s-password-field>`, `<s-search-field>`, `<s-color-field>`, `<s-color-picker>`, `<s-date-picker>` | Typed text-field variants — share `label`/`placeholder` with `<s-text-field>`. Use when input type matters for validation/autocomplete. |

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
| `<s-table-header>` | Column header | `list-slot` (`primary`/`labeled`/`inline`/`secondary`) controls responsive behavior. `format="numeric"` or `"currency"` for alignment. |

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

