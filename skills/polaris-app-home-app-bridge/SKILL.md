---
name: polaris-app-home-app-bridge
description: "Shopify App Bridge surface for Polaris App Home — `useAppBridge` hook, all `shopify.*` APIs, and App Bridge web components (`<s-app-nav>`, `<s-app-window>`, `<form data-save-bar>`). TRIGGER when: code calls `shopify.*` or `useAppBridge`; user mentions any App Bridge feature (toast, modal, save bar, scanner, scopes, idToken, picker, intents, etc.)."
model: opus
---

# Polaris App Home — App Bridge

Reference for the App Bridge surface inside `polaris-app-home`: the `useAppBridge` React hook, all `shopify.*` API namespaces, and the two App Bridge web components that don't validate as JSX (`<s-app-nav>`, `<s-app-window>`). Save bar is documented end-to-end here (declarative form attribute + programmatic API).

## When to use

YES: Code calls a `shopify.*` API (toast, modal, save bar, scanner, idToken, picker, scopes, intents, web vitals, POS).
YES: Code uses `useAppBridge()` from `@shopify/app-bridge-react`.
YES: Adding `<s-app-nav>` (top-of-app navigation) or `<s-app-window>` (embedded iframe).
YES: Setting up a save bar (`<form data-save-bar>`) or programmatic save bar control.
NO: Writing Polaris `<s-page>`, `<s-section>`, `<s-button>`, etc. markup — use `polaris-app-home-web-components`.
NO: Title bar — title bar is configured via `<s-page>` slots in `polaris-app-home-web-components` (there is no `shopify.titleBar` namespace).

## Instructions

1. Find the API / hook / component in the appendix below. If missing, route through `shopify-dev-mcp` → `search_docs_chunks` with `api_name: "polaris-app-home"` and a doc-path hint (e.g. `"save bar API"`, `"resource picker"`, `"useAppBridge"`).
2. Write code following the [Rules](#rules).
3. **Validation caveat:** `validate_component_codeblocks` does NOT type-check App Bridge web components in JSX. `<s-app-nav>`, `<s-app-window>`, and `<s-link rel="home">` will fail JSX validation with `Property 's-app-nav' does not exist on type 'JSX.IntrinsicElements'`. **Treat these specific failures as expected, not errors.** Polaris `<s-*>` markup in the same file should still be validated normally.
4. If `validate_component_codeblocks` flags a Polaris component or prop (not an App Bridge component listed above), fix and re-validate. Max 2 attempts. If still failing, surface the error via the `AskUserQuestion` tool with options: "Retry with hints", "Skip validation", "Abort". Recommended: "Retry with hints".

## Rules

- **Use `useAppBridge()` in React, `window.shopify` outside React.** `useAppBridge()` from `@shopify/app-bridge-react` returns the `shopify` global (or an SSR-safe proxy in non-browser env). They're the same object at runtime. Prefer the hook in React code for SSR safety.
- **App Bridge web components don't validate as JSX.** `<s-app-nav>`, `<s-app-window>`, `<s-link rel="home">` will fail `validate_component_codeblocks`. Use raw HTML, the `@shopify/app-bridge-react` wrappers (`<NavMenu>`, `<TitleBar>`, `<SaveBar>`), or accept the validation warning.
- **`<s-*>` is canonical, `<ui-*>` is legacy.** Current App Home docs use `<s-app-nav>` and `<s-app-window>`. The legacy `<ui-nav-menu>` / `<ui-save-bar>` / `<ui-title-bar>` names are still emitted by `@shopify/app-bridge-react` wrappers. They run, but only `<s-*>` is in current docs.
- **No `shopify.appWindow` namespace exists.** Control `<s-app-window>` via DOM instance methods on the element ref (`.show()`, `.hide()`, `.toggle()`) or `commandFor` on a trigger button.
- **No `shopify.titleBar`, `shopify.action`, `shopify.clipboard`, `shopify.geolocation`, `shopify.nfc`, `shopify.share`, `shopify.print` namespaces.** `share` and `print` ARE available — but as the standard browser APIs `navigator.share()` and `window.print()`, intercepted by App Bridge on mobile/POS.
- **`shopify.loading` is a function, not an object.** Call `shopify.loading(true)` / `shopify.loading(false)`. There is no `.start()` / `.stop()`.
- **`shopify.modal.*` targets `<s-modal>` (Polaris).** Confirmed via docs. Element ref methods (`el.showOverlay()`, etc.) are equivalent.
- **Resource Picker `action` enum is `'add' | 'select'`** with `'add'` default. Not `'cancel'` / `'submit'`.
- **`<s-link rel="home">` in `<s-app-nav>` fails JSX validation by design.** Render via raw HTML or `<NavMenu>` React wrapper. The `rel` attribute is not in the Polaris `<s-link>` schema.

---

## App Bridge React hook

| Hook | Signature | Returns | Notes |
|---|---|---|---|
| `useAppBridge()` | `() => Shopify` | The `shopify` global (or SSR-safe proxy) | Import: `import { useAppBridge } from '@shopify/app-bridge-react'`. Requires `@shopify/app-bridge-react@v4` AND the `app-bridge.js` script tag. Returns the same object as `window.shopify`. Safe during SSR. |

Doc: `/docs/api/app-home/apis/react-hooks/useappbridge`

## Authentication & Data APIs

| Namespace / method | Signature | Returns | Notes |
|---|---|---|---|
| `shopify.app.extensions()` | `() => Promise<ExtensionInfo[]>` | Array of `{handle, type, activations}`. `type` is `'ui_extension' \| 'theme_app_extension'` | Read-only discovery. Theme app extension data sourced from published theme only. Empty array if no extensions. |
| `shopify.config` | property (synchronous) | `{ apiKey, shop, host, locale, appOrigins, disabledFeatures, debug: { webVitals } }` | `apiKey` set via `<meta name="shopify-api-key">`. `shop`/`host`/`locale` set automatically by host. `disabledFeatures` supports `'fetch'` and `'auto-redirect'`. |
| `shopify.environment` | property (synchronous booleans) | `{ embedded, intent, mobile, pos }` | Sync access. Use to gate features by platform. `intent` indicates the app is running as an intent target (paired with `shopify.intents.invoke`). |
| `fetch()` (global, intercepted) | standard `fetch(input, init?)` | `Promise<Response>` | Auto-injects `Authorization: Bearer <idToken>` for app-domain requests; injects `Accept-Language`. Use `shopify:admin/api/graphql.json` URL scheme for direct Admin API. Disable interception via `disabledFeatures: ['fetch']`. Direct API also requires `embedded_app_direct_api_access = true` in `shopify.app.toml`. |
| `shopify.idToken()` | `() => Promise<string>` | JWT ID Token (OpenID Connect) | App Bridge auto-includes ID token in fetch interceptor. Call directly only for non-fetch flows (WebSockets, third-party services). |
| `shopify.scopes.query()` | `() => Promise<ScopesDetail>` | `{ granted: string[], required: string[], optional: string[] }` | |
| `shopify.scopes.request(scopes)` | `(scopes: string[]) => Promise<ScopesRequestResponse>` | `{ result: 'granted-all' \| 'declined-all', detail }` | Scopes must be declared `optional` in app config. Opens permission grant modal. |
| `shopify.scopes.revoke(scopes)` | `(scopes: string[]) => Promise<ScopesRevokeResponse>` | `{ detail }` | Only `optional` scopes can be revoked. Required scopes cannot. |
| `shopify.user()` | `() => Promise<AdminUser \| POSUser>` | `AdminUser = { accountAccess }`. `POSUser = { id, firstName, lastName, email, accountAccess, accountType }` | Response shape varies by surface (admin vs POS). |

## UI & Interactions APIs

| Namespace / method | Signature | Returns | Notes |
|---|---|---|---|
| `shopify.toast.show(message, opts?)` | `(message: string, opts?) => string` | toast id | `ToastOptions = { action?, duration?, isError?, onAction? }` |
| `shopify.toast.hide(id)` | `(id: string) => void` | void | Auto-hides after `duration`. |
| `shopify.modal.show(id)` | `(id: string) => Promise<void>` | Promise<void> | Targets `<s-modal id="...">`. Equivalent to `el.showOverlay()`. |
| `shopify.modal.hide(id)` | `(id: string) => Promise<void>` | Promise<void> | Equivalent to `el.hideOverlay()`. |
| `shopify.modal.toggle(id)` | `(id: string) => Promise<void>` | Promise<void> | Equivalent to `el.toggleOverlay()`. |
| `shopify.resourcePicker(opts)` | `(opts) => Promise<Selection[] \| undefined>` | Array of resources or `undefined` if cancelled | Options: `type: 'product' \| 'variant' \| 'collection'` (required); `action: 'add' \| 'select'` (default `'add'`); `multiple: boolean \| number`; `filter`; `selectionIds`; `query`. |
| `shopify.picker(opts)` | `(opts) => Promise<Picker>` (with `.selected`) | Picker; `.selected` is array of chosen IDs | For app-specific data, NOT Shopify resources. Options: `heading` (required); `items: PickerItem[]` (required); `headers?`; `multiple?: boolean \| number`. |
| Navigation API | Anchor-based + JS APIs | n/a | `<a href="shopify://admin/products">` for admin pages. `<a href="/path" target="_self">` relative. `target="_blank"` external. JS: `open(url, target)`, `history.pushState/replaceState`, `navigation.navigate(url, { history: 'push' \| 'replace' })`. **No `shopify.navigate()`.** |
| `shopify.loading(isLoading)` | `(isLoading: boolean) => void` | void | Toggles top-of-admin loading bar. **Function, not `.start()` / `.stop()`.** |
| `shopify.saveBar.show(id)` | `(id: string) => Promise<void>` | Promise<void> | `id` is the `<form id="...">` id. |
| `shopify.saveBar.hide(id)` | `(id: string) => Promise<void>` | Promise<void> | |
| `shopify.saveBar.toggle(id)` | `(id: string) => Promise<void>` | Promise<void> | |
| `shopify.saveBar.leaveConfirmation()` | `() => Promise<void>` | Promise<void> | Resolves once merchant confirms or no save bar visible. **Call before programmatic navigation when a dirty form may exist.** |
| `shopify.intents.invoke(query, opts?)` | `(query: string \| object, opts?) => Promise<Activity>` | Activity handle with `.complete: Promise<{ code, ... }>` | String form: `'create:shopify/Product'` or `'edit:shopify/Product,gid://shopify/Product/123'`. Object form: `{ action, type, value, data }`. `data` carries type-specific extras (discount type, parent product for variants, definition type for metaobjects). |
| `shopify.reviews.request()` | `() => Promise<ReviewRequestResponse>` | `{ success, code, message }` | Decline codes: `'mobile-app' \| 'already-reviewed' \| 'annual-limit-reached' \| 'cooldown-period' \| 'merchant-ineligible' \| 'recently-installed' \| 'already-open' \| 'open-in-progress' \| 'cancelled'`. Rate-limited; bypass on dev stores. |
| `shopify.support.registerHandler(cb)` | `(cb \| null) => Promise<void>` | Promise<void> | Requires Support link extension pointing at a page in your app — without that, callback ignored. |

## Device & Platform APIs

| Namespace / method | Signature | Returns | Notes |
|---|---|---|---|
| `shopify.scanner.capture()` | `() => Promise<{ data: string }>` | `{ data: string }` (scanned barcode) | **POS only.** Mobile-only feature in Shopify POS. Throws/rejects on cancel/failure. |
| `navigator.share(data)` | standard Web Share API | `Promise<void>` | Intercepted by App Bridge on mobile/POS to invoke native share sheet. **`files` property NOT supported.** Use try/catch. **Not under `shopify.*`.** |
| `print()` (or `window.print()`) | standard | void | Intercepted on Shopify Mobile/POS. **Not under `shopify.*`.** |
| `shopify.webVitals.onReport(cb)` | `(cb \| null) => Promise<void>` | Promise<void> | Pass `null` to unregister. Callback receives `{ metrics: WebVitalsMetric[] }` where each metric has `{ name: 'LCP'\|'FCP'\|'CLS'\|'INP'\|'TTFB'\|'FID', value, id, country? }`. |
| `shopify.pos.cart` | `PosCart` | various Promise<void> | **POS only.** Methods: `addLineItem`, `addLineItemProperties`, `addCartProperties`, `addCustomSale`, `addAddress`, `applyCartCodeDiscount`, `applyCartDiscount`, plus more. Recommend POS UI extensions over App Home for POS work. |
| `shopify.pos.close()` | `() => Promise<void>` | Promise<void> | **POS only.** Closes app, returns to POS screen. |
| `shopify.pos.device` | `PosDevice` | `{ name, serialNumber, ... }` | **POS only.** |
| `shopify.pos.location` | `PosLocation` | `{ id, name, address, status }` | **POS only.** |

## App Bridge Web Components

These are **NOT typed by `validate_component_codeblocks`** — JSX validation will reject them with `Property '<tag>' does not exist on type 'JSX.IntrinsicElements'`. That's expected. Use raw HTML, the React wrappers from `@shopify/app-bridge-react`, or a JSX type augmentation.

### `<s-app-nav>` — top-of-app navigation

| Prop | Type | Required | Notes |
|---|---|---|---|
| (children) | `<s-link>` elements | yes | Each link is one nav item. |

`<s-link>` child props inside `<s-app-nav>`:

| Prop | Type | Required | Notes |
|---|---|---|---|
| `href` | string | yes | Relative app path, e.g. `/products`. |
| `children` | string | no | Visible label (1-2 words, nouns). |
| `rel` | `'home'` | no | Marks default landing page. Hidden from menu. Only one allowed. **`rel="home"` fails JSX validation** — use raw HTML or `<NavMenu>` React wrapper. |

- **No nesting.** Only one nav level.
- **Programmatic navigation goes through the Navigation API**, not a method on `<s-app-nav>`.
- **No `shopify.appNav` namespace.**
- **React wrapper:** `<NavMenu>` from `@shopify/app-bridge-react`.

### `<s-app-window>` — embedded iframe

| Prop | Type | Required | Notes |
|---|---|---|---|
| `src` | string | yes | URL of the route to load inside the iframe. |
| `id` | string | no | Used with `commandFor` and `document.getElementById()`. |

- **No content slots** — content comes from the `src` iframe.
- **DOM instance methods** (call on element ref):
  - `show(): Promise<void>` — opens.
  - `hide(): Promise<void>` — closes; resolves once fully hidden. Forms with `data-save-bar` will prompt before close.
  - `toggle(): Promise<void>` — toggles.
  - `addEventListener('show' | 'hide', listener)` — lifecycle events.
  - `contentWindow: Window | null` — inner iframe `Window`, or `null` when closed. Use for `postMessage()`.
- **Events:** `show`, `hide`.
- **No `shopify.appWindow` namespace exists.**
- **Polaris `<s-modal>` is recommended over `<s-app-window>` for most dialogs.**

## Save Bar (form attribute + API)

The save bar has two surfaces — a declarative form attribute and a programmatic API. Both target the same UI element.

### Declarative — `<form data-save-bar>`

| Attribute | Type | Required | Notes |
|---|---|---|---|
| `data-save-bar` | boolean | yes (to enable) | Auto-shows save bar when any input changes from initial state. Auto-hides on submit/reset. |
| `data-discard-confirmation` | boolean | no | Adds confirmation step before reset. |

| Handler | Signature | Notes |
|---|---|---|
| `onSubmit` | `(event: SubmitEvent) => void` | Save click. Use `event.preventDefault()` for custom async logic. |
| `onReset` | `(event: Event) => void` | Discard click. `event.preventDefault()` to keep form state. |

### Programmatic — `shopify.saveBar.*`

| Method | Signature | Notes |
|---|---|---|
| `shopify.saveBar.show(id)` | `(id: string) => Promise<void>` | `id` is the `<form id="...">` id. |
| `shopify.saveBar.hide(id)` | `(id: string) => Promise<void>` | |
| `shopify.saveBar.toggle(id)` | `(id: string) => Promise<void>` | |
| `shopify.saveBar.leaveConfirmation()` | `() => Promise<void>` | Resolves once merchant confirms or no save bar is visible. **Call before programmatic navigation when a dirty form may exist.** |

- **Validator does not type the `data-save-bar` form attribute** — passing the form through `validate_component_codeblocks` will not error on this attribute, but it also won't catch typos.
- **There is no `<s-save-bar>` element.** Don't generate it.
- **React wrapper:** `<SaveBar>` from `@shopify/app-bridge-react` (legacy form, still works).

## Title Bar (note)

There is **no `<s-title-bar>` element and no `shopify.titleBar` namespace.** The title bar is configured via `<s-page>` props (`heading`) and slots (`primary-action`, `secondary-actions`, `breadcrumb-actions`, `accessory`). See `polaris-app-home-web-components` → `<s-page>`.

The React wrapper `<TitleBar>` from `@shopify/app-bridge-react` is still valid (it has a `subtitle` prop that the underlying `<s-page>` does not).
