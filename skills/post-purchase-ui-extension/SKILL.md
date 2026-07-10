---
name: post-purchase-ui-extension
description: "SDK reference for `@shopify/post-purchase-ui-extensions-react` — Shopify's post-purchase upsell surface (the screen between payment and the thank-you page). Distinct from modern `<s-*>` checkout-extensions, which have no post-purchase target. TRIGGER when: code imports `@shopify/post-purchase-ui-extensions-react`; user mentions post-purchase offer, post-purchase page, post-purchase upsell, post-purchase-ui-extensions, ShouldRender, applyChangeset, or `Checkout::PostPurchase::*`; user edits files under `extensions/*post-purchase*/`."
compatibility: Requires Node.js + tsc
model: opus
---

# Post-Purchase UI Extension

Component catalog, lifecycle contract, and sandbox rules for `@shopify/post-purchase-ui-extensions-react` (post-purchase upsell surface, npm `0.13.5`, package in maintenance — no newer version exists; the modern `<s-*>` checkout-extensions SDK has no post-purchase target as of writing).

## ⚠️ MANDATORY: Validate with tsc (do not skip)

Run after writing or editing any post-purchase JSX:

```bash
cd extensions/<your-extension>
npx tsc --noEmit
```

TypeScript resolves types automatically via the bundled `.d.ts` at `node_modules/@shopify/post-purchase-ui-extensions-react/build/ts/index.d.ts`. If types fail twice on the same artifact, stop and surface the error to the user.

**NEVER call `validate_component_codeblocks`, `validate_graphql_codeblocks`, or `search_docs_chunks` for this SDK.** The Shopify Dev MCP doesn't index `@shopify/post-purchase-ui-extensions-react`. The validator's `polaris-checkout-extensions` enum value covers the modern `@shopify/ui-extensions` web-component SDK only and rejects every post-purchase component (`BlockStack`, `Button`, …) as "not a Polaris web component."

## ⚠️ Skip if a different surface

- **Admin App Home `<s-*>` markup** → use `shopify-polaris-app-home` instead.
- **Modern checkout extensions** (`@shopify/ui-extensions-react`, `<s-*>` web components) → use `shopify-polaris-checkout-extensions` instead.
- **Customer account extensions** → use `shopify-polaris-customer-account-extensions` instead.

## Doc lookup (WebFetch only)

The MCP doesn't index this SDK — use WebFetch:

- **Component props:** `https://shopify.dev/docs/api/checkout-extensions/post-purchase/components/<name>` (lowercase — PascalCase URLs return 404, e.g. `/components/blockstack` works, `/components/BlockStack` does not)
- **Lifecycle, `useExtensionInput`, `Changeset`, `InputData`, `ChangesetErrorCode`:** `https://shopify.dev/docs/api/checkout-extensions/post-purchase/api`
- **End-to-end tutorials:** `https://shopify.dev/docs/apps/build/checkout/product-offers/build-a-post-purchase-offer` and `https://shopify.dev/docs/apps/build/checkout/product-offers/create-a-post-purchase-subscription`
- **UX guidance** (only when working on copy, layout, or offer framing — not for API/prop questions): `https://shopify.dev/docs/apps/build/checkout/product-offers/ux-for-post-purchase-product-offers` and `https://shopify.dev/docs/apps/build/checkout/product-offers/ux-for-post-purchase-subscriptions`

If a component, prop, lifecycle field, or error code is missing from the [Component Catalog](#component-catalog) or [Lifecycle Contract](#lifecycle-contract) below, WebFetch the canonical reference.

## Rules

- **Two extension points, two phases.** `extend("Checkout::PostPurchase::ShouldRender", …)` is a data-prefetch hook; `render("Checkout::PostPurchase::Render", App)` is the React mount. Render runs only if ShouldRender returned `{ render: true }`. See [Lifecycle Contract](#lifecycle-contract).
- **`storage.update(data)` in ShouldRender; `storage.initialData` in Render.** Storage is the only hand-off between the two phases — they run in separate JS contexts.
- **`applyChangeset` takes a signed JWT string, not a Changeset object.** Sign the changeset on your backend with the app's API secret, return the token to the extension, then call `await applyChangeset(token)`. Never sign client-side.
- **Always call `done()`, including on error paths.** Documented behavior: `done()` "indicates that the extension has finished running" and "redirects customers to the Order status page." Build-guide code samples call it in both accept and decline branches. Operational rule (not stated in shopify.dev): if an accept handler throws or rejects before `done()` runs, the buyer is stuck on a blank screen — wrap accept handlers in try/finally to guarantee the call.
- **Treat `ShouldRender` as potentially called more than once per checkout.** The shopify.dev pages do not document call frequency. Operational observation in production: it can fire on payment-page load and again after the buyer clicks Pay. Make the handler idempotent (backend dedupe of identical fetches keyed by `referenceId`).
- **Sandbox: no DOM, no CSS, no `window`, no external scripts.** All visual customization happens through component props. There is no `<style>`, no `className`, no inline `style={…}`. Spacing comes from prop tokens — but the scale **differs per component** (see [Spacing scales](#spacing-scales)).
- **`.jsx` / `.js` extension required in every import.** The Shopify CLI bundler does not auto-resolve. `import { X } from "./foo"` fails; `import { X } from "./foo.jsx"` works.
- **Only import what the SDK re-exports from `"react"`.** The runtime bundles its own React — importing additional React entry points causes duplicate-React errors. `useState`, `useEffect`, etc. work because they pass through.
- **Validate with `tsc`, not the MCP.** See [MANDATORY block](#mandatory-validate-with-tsc-do-not-skip) above.

## Common Patterns

Generic SDK patterns. Repo-specific architecture (layouts/templates/components, normalize functions, config/token systems) lives in the consuming repo's `architecture.md`, not here.

### Boilerplate entry point
The two-phase contract — every post-purchase extension starts with this skeleton.
```jsx
import { extend, render } from "@shopify/post-purchase-ui-extensions-react";

extend("Checkout::PostPurchase::ShouldRender", async ({ inputData, storage }) => {
  const data = await fetchOffer(inputData);    // your backend
  if (!data) return { render: false };
  await storage.update(data);
  return { render: true };
});

render("Checkout::PostPurchase::Render", App);

function App({ storage, applyChangeset, done }) {
  const offer = storage.initialData;
  return <BlockStack spacing="loose">{/* … */}</BlockStack>;
}
```

### Loading state on accept Button
`Button` has a built-in `loading` prop — flip it on press to disable double-clicks during the sign-changeset round trip. No reset needed; `done()` navigates away.
```jsx
const [loading, setLoading] = useState(false);
<Button
  loading={loading}
  loadingLabel="Processing"
  onPress={async () => {
    setLoading(true);
    const token = await signChangeset(variantId);
    await applyChangeset(token);
    done();
  }}
>
  Add to order
</Button>
```

### Image with locked aspect ratio
Use `aspectRatio` + `fit="cover"` to prevent layout shift and align cards in a `Tiles` grid when source images have varying intrinsic ratios.
```jsx
<Image source={url} description={alt} aspectRatio={1} fit="cover" />
```

### Heading semantics via HeadingGroup
Heading levels are derived from `HeadingGroup` nesting depth — never set `level` manually unless you need to override visuals.
```jsx
<HeadingGroup>
  <Heading>Section title</Heading>
  <HeadingGroup>
    <Heading>Subsection title</Heading>
  </HeadingGroup>
</HeadingGroup>
```

---

## Lifecycle Contract

### Extension points

| Point | String | Purpose |
|---|---|---|
| ShouldRender | `Checkout::PostPurchase::ShouldRender` | Data prefetch. Decide whether to render. |
| Render | `Checkout::PostPurchase::Render` | Mount the React tree. |

### ShouldRender API

```ts
(api: PostPurchaseShouldRenderApi) => { render: boolean } | Promise<{ render: boolean }>
```

`api` exposes `inputData: InputData`, `storage`, plus `version` / `locale` / `extensionPoint` from the standard surface.

- `storage.update(data: any): Promise<void>` — persist data for the Render phase. Returns a Promise — `await` it before returning.
- Return `{ render: true }` to mount, `{ render: false }` to skip silently. May return synchronously or as a `Promise`.

### Render API

```ts
render("Checkout::PostPurchase::Render", (api: PostPurchaseRenderApi) => ReactElement)
```

| Field | Type | Use |
|---|---|---|
| `inputData` | `InputData` | Same shape as ShouldRender. |
| `storage.initialData` | `unknown` | Data written by ShouldRender via `storage.update`. Read-only. |
| `calculateChangeset` | `(changeset: Readonly<Changeset> \| string) => Promise<CalculateChangesetResult>` | Preview cost impact without applying. Pass either a raw `Changeset` object or the signed JWT string. |
| `applyChangeset` | `(changeset: string, options?: ApplyChangesetOptions) => Promise<ApplyChangesetResult>` | Apply the order edit and charge the buyer. The `changeset` parameter is a JWT string signed by your backend with the app secret — despite the name, this overload does not accept a raw object. |
| `done` | `() => Promise<void>` | Navigate to thank-you page. Always call this, success or error. |
| `version` / `locale` / `extensionPoint` | from `StandardApi` | Available alongside `inputData`. |

### InputData

| Field | Type |
|---|---|
| `extensionPoint` | `string` |
| `initialPurchase` | `Purchase` (referenceId, customerId?, destinationCountryCode?, totalPriceSet, lineItems[]) |
| `locale` | `string` |
| `shop` | `Shop` (id: number, domain, metafields) |
| `token` | `string` (JWT — pass to your backend for verification) |
| `version` | `string` (current value: `'unstable'`) |

`LineItem`: `product`, `quantity`, `totalPriceSet`, `sellingPlanId?`. `Product`: `id`, `title`, `variant`, `metafields`. `Metafield.value` is `string | number`; `valueType` is `'integer' | 'string' | 'json_string'`.

### Changeset shape

```ts
Changeset { changes: Changes }
Changes = (AddVariantChange | AddShippingLineChange | SetMetafieldChange | AddSubscriptionChange)[]
```

### ApplyChangesetOptions

| Option | Type | Use |
|---|---|---|
| `buyerConsentToSubscriptions?` | `boolean` | Set when changes include `add_subscription`; pair with `BuyerConsent` component. Optional in the type, but required by the server for subscription changes. |

### ChangesetErrorCode

`payment_required` · `insufficient_inventory` · `changeset_already_applied` · `unsupported_payment_method` · `invalid_request` · `server_error` · `buyer_consent_required` · `subscription_vaulting_error` · `subscription_contract_creation_error` · `subscription_no_shipping_address_error` · `subscription_limit_error` · `order_released_error`

---

## Component Catalog

29 components total, served by 28 doc URLs under `/components/<name>` (lowercase). `FormLayoutGroup` shares the `formlayout` page rather than having its own URL — when looking it up, fetch `/components/formlayout`.

All importable from `@shopify/post-purchase-ui-extensions-react`.

### Spacing scales

There is no single "spacing scale" — three different scales coexist. Match the literal exactly to the consumer's `.d.ts`:

| Scale | Allowed values | Used by |
|---|---|---|
| Stack scale | `'xtight' \| 'tight' \| 'loose' \| 'xloose'` | `BlockStack.spacing`, `InlineStack.spacing`, `Bookend.spacing` |
| Stack scale + `none` | `'none' \| 'xtight' \| 'tight' \| 'loose' \| 'xloose'` | `Tiles.spacing` |
| Compact scale | `'none' \| 'tight' \| 'loose'` | `TextContainer.spacing`, `CalloutBanner.spacing` |
| View padding scale | `'extraTight' \| 'tight' \| 'base' \| 'loose' \| 'extraLoose'` | `View.inlinePadding`, `View.blockPadding` |

`xtight`/`xloose` and `extraTight`/`extraLoose` are NOT interchangeable — each is rejected by the component that doesn't list it.

### Layout & Structure

| Component | Purpose | Key Props / Gotchas |
|---|---|---|
| `BlockStack` | Vertical stack | `spacing`: stack scale (no `none`). `alignment`: `'leading' \| 'center' \| 'trailing'`. |
| `InlineStack` | Horizontal row | `spacing`: stack scale. `alignment`: `'leading' \| 'center' \| 'trailing' \| 'baseline'`. |
| `Bookend` | Pin first/last child to intrinsic size, fill middle | `leading?: boolean`, `trailing?: boolean`. `spacing`: stack scale. `alignment`: `'leading' \| 'center' \| 'trailing' \| 'baseline'`. |
| `Tiles` | Equal-size grid, wraps and stacks responsively | `maxPerLine?: number`. `breakAt?: number` (px width below which tiles stack). `spacing`: stack scale + `'none'`. `alignment`: `'leading' \| 'center' \| 'trailing' \| 'baseline'`. Direct children stretch — wrap a child in `View` to keep its intrinsic size. |
| `Layout` | Multi-section page scaffold with media-queried sizes | `maxInlineSize?: number` (≤1 = %, >1 = px). `sizes?: Size[]` where `Size = 'auto' \| 'fill' \| number`. `media?: Media[]` where `Media = { viewportSize: 'small' \| 'medium' \| 'large'; maxInlineSize?: number; sizes?: Size[] }`. `inlineAlignment?: 'leading' \| 'trailing'`. `blockAlignment?: 'center' \| 'trailing'`. **No `spacing` prop exists** on `LayoutProps` despite appearing in some doc code samples — using it is a TS error. |
| `View` | Generic container that does NOT stretch | `inlinePadding` / `blockPadding`: View padding scale (`'extraTight' \| 'tight' \| 'base' \| 'loose' \| 'extraLoose'`). Note camelCase — NOT `xtight`/`xloose`. Use to opt out of `Tiles`/`Layout` stretching. |
| `Separator` | Visual divider | `direction`: `'horizontal'` (default) / `'vertical'`. `width`: `'thin' \| 'medium' \| 'thick' \| 'xthick'`. |

### Typography

| Component | Purpose | Key Props / Gotchas |
|---|---|---|
| `Heading` | Section title | `level?: 1 \| 2 \| 3` — visual override only; semantic level comes from `HeadingGroup` nesting. `role?: 'presentation'` strips semantics, keeps styling. |
| `HeadingGroup` | Increments heading level for nested children | No props. Wrap children that contain their own `Heading` to bump them down a level semantically. |
| `Text` | Inline styled text | `size?: 'small' \| 'medium' \| 'large' \| 'xlarge'`. `emphasized?: boolean`, `subdued?: boolean`. `id?: string`. `appearance?: 'critical' \| 'warning' \| 'success'`. `role`: string `'address'` or `'deletion'` (use `deletion` for strikethrough on original prices), or an object: `{ type: 'abbreviation'; for?: string }`, `{ type: 'directional-override'; direction: 'ltr' \| 'rtl' }` (direction is required), `{ type: 'datetime'; machineReadable?: string }`. Inline only — wrap in `TextBlock` or a stack to break to a new line. |
| `TextBlock` | Block-level paragraph | `size?: 'small' \| 'medium' \| 'large' \| 'xlarge'`. `emphasized?: boolean`, `subdued?: boolean`. `id?: string`. `appearance?: 'critical' \| 'warning' \| 'success'`. No `role` prop. |
| `TextContainer` | Vertical spacing wrapper for text elements | `spacing?: 'none' \| 'tight' \| 'loose'` (compact scale — `xtight`/`xloose` are NOT accepted here). `alignment?: 'leading' \| 'center' \| 'trailing'`. |

### Actions

| Component | Purpose | Key Props / Gotchas |
|---|---|---|
| `Button` | Primary action | `onPress?(): void` (optional in the type — provide if not using `submit` or `to`). `submit?: boolean` (form submit). `to?: string` (renders as Link). `subdued?: boolean` (secondary look), `plain?: boolean` (link-styled). `loading?: boolean` + `loadingLabel?: string`. `disabled?: boolean`. **No `variant`/`tone` props** — emphasis is via `subdued`/`plain`. |
| `ButtonGroup` | Inline-stacked buttons with auto-spacing | No props. Wraps two or more `Button`s. |
| `Link` | Navigation | `to?: string` and/or `onPress?(): void` — provide at least one. `external?: boolean` opens in new tab. `id?: string` (target for accessibility-label associations). Not a button — use `Button` for actions. |

### Forms

| Component | Purpose | Key Props / Gotchas |
|---|---|---|
| `Form` | Form wrapper with implicit-submit-on-Enter | `onSubmit(): void` required. `disabled?: boolean`. `implicitSubmit?: boolean \| string` (string = a11y label for screen-reader-only submit button). No `<form>` HTTP submission — handle in `onSubmit`. |
| `FormLayout` | Vertical-stacked field layout | No props. Children stack on the block axis. |
| `FormLayoutGroup` | Inline-grouped fields within a `FormLayout` | No props. Fields appear side-by-side with equal spacing. Lives in the same `.d.ts` file as `FormLayout`. |
| `TextField` | Single-line input | `label: string` (required, doubles as placeholder when empty). `value?: string`, `onChange?(value: string): void` (fires on commit/blur). `onInput?(value: string): void` (fires every keystroke — drive controlled state from `onInput`, not `onChange`). `type?: 'text' \| 'email' \| 'number' \| 'telephone'`. `name?: string` (form key). `id?: string`. `required?: boolean` (semantic only; does not auto-error). `error?: string`. `multiline?: boolean`. `autocomplete?: Autocomplete \| boolean`. `tooltip?: { label: string; content: string }`. `onFocus?(): void`, `onBlur?(): void`. |
| `Select` | Dropdown | `label: string` (required). `options: { value: string; label: string; disabled?: boolean }[]`. `value?: string`, `onChange?(value: string): void`. `placeholder?: string`. `id?: string`, `name?: string`. `required?: boolean`. `disabled?: boolean` (on the Select itself, not just options). `error?: string`. `autocomplete?: Autocomplete \| boolean`. |
| `Checkbox` | Boolean toggle | `checked?: boolean` (preferred) or `value?: boolean` — `checked` takes precedence when both are set. `onChange?(value: boolean): void`. `disabled?: boolean`, `error?: string`. `id?: string`, `name?: string`, `accessibilityLabel?: string`. |
| `Radio` | Single radio button | `name: string` (required — same `name` groups options). `checked?: boolean` / `value?: boolean`. `onChange?(value: boolean): void`. `disabled?: boolean`. `id?: string`, `accessibilityLabel?: string`. |
| `BuyerConsent` | Subscription consent checkbox | `policy: 'subscriptions'`. `checked: boolean` (required), `onChange(value: boolean): void` (required — unlike other form components). `error?: string`. Required when applying an `add_subscription` change with `applyChangeset(token, { buyerConsentToSubscriptions: true })`. |

### Feedback & Status

| Component | Purpose | Key Props / Gotchas |
|---|---|---|
| `Banner` | Status / system message | `title?: string`. `status?: 'info' \| 'success' \| 'warning' \| 'critical'` (default `'info'`). `collapsible?: boolean`, `iconHidden?: boolean`. **For status reporting** — not for promotional copy. |
| `CalloutBanner` | Promotional offer header | `title?: string`. `background?: 'secondary' \| 'transparent'` (default `'secondary'`). `border?: 'none' \| 'block'` (default `'block'`). `alignment?: 'leading' \| 'center' \| 'trailing'` (default `'center'`). `spacing?: 'none' \| 'tight' \| 'loose'` (compact scale — `xtight`/`xloose` are NOT accepted; default `'tight'`). **For limited-time-offer framing** — distinct from `Banner`. |
| `Spinner` | Loading indicator | `size?: 'small' \| 'large'`. `color?: 'inherit'`. Children = a11y fallback for reduced-motion users. |

### Media

| Component | Purpose | Key Props / Gotchas |
|---|---|---|
| `Image` | Responsive image | `source: string` (required). `description?: string` (alt; default `''`). `sources?: { source: string; viewportSize?: 'small' \| 'medium' \| 'large'; resolution?: 1 \| 1.3 \| 1.5 \| 2 \| 2.6 \| 3 \| 3.5 \| 4 }[]` for responsive variants — `resolution` is a constrained numeric literal union, not any number. `aspectRatio?: number` — sets height from width to prevent layout shift. `fit?: 'cover' \| 'contain'` (pair with `aspectRatio` to avoid stretch). `loading?: 'eager' \| 'lazy'`. `bordered?: boolean`, `decorative?: boolean`. |

### Accessibility

| Component | Purpose | Key Props / Gotchas |
|---|---|---|
| `HiddenForAccessibility` | Hide children from a11y tree but show visually | No props. Use for purely decorative or duplicated content. |
| `VisuallyHidden` | Hide visually but keep available to screen readers | No props. Use for screen-reader-only labels. |
