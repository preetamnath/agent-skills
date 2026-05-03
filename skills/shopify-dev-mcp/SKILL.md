---
name: shopify-dev-mcp
description: "Routes Shopify Dev MCP calls for surfaces NOT covered by the bundled Shopify skills: storefront-graphql, customer, partner, payments-apps, functions, hydrogen, liquid, custom-data. Also the fallback validator when shopify-admin / shopify-polaris-* bundled scripts are unavailable. SKIP for Admin GraphQL or App Home markup if those skills are installed (their bundled scripts are faster). SKIP entirely for @shopify/post-purchase-ui-extensions-react — the MCP doesn't index that legacy SDK."
compatibility: Requires Shopify Dev MCP server
allowed-tools: mcp__shopify-dev-mcp__*
---

# Shopify Dev MCP

Routes MCP tool calls for Shopify surfaces. Standard lookups, not deep reasoning.

## ⚠️ Skip if a bundled skill applies

The 7 official Shopify skills ship local validators (`scripts/search_docs.mjs`, `scripts/validate.mjs`) that are faster than the MCP and don't require a server round-trip:

| Surface | Use this skill instead |
|---|---|
| Admin GraphQL | `shopify-admin` |
| App Home `<s-*>` markup | `shopify-polaris-app-home` |
| Admin Action/Block extensions | `shopify-polaris-admin-extensions` |
| Modern checkout `<s-*>` markup | `shopify-polaris-checkout-extensions` |
| Customer Account UI | `shopify-polaris-customer-account-extensions` |
| App Store pre-submission review | `shopify-app-store-review` |
| `shopify.app.toml` / CLI workflows | `shopify-use-shopify-cli` |

Use `shopify-dev-mcp` ONLY when:
- The surface isn't in the table above (`storefront-graphql`, `customer`, `partner`, `payments-apps`, `functions`, `hydrogen`, `liquid`, `custom-data`).
- You're cross-referencing schemas across two surfaces in one conversation.
- The bundled script for an installed skill is unavailable or erroring.

## ⚠️ NOT for legacy post-purchase

The MCP does NOT index `@shopify/post-purchase-ui-extensions-react`. `validate_component_codeblocks` rejects every legacy post-purchase component by design — the validator's `polaris-checkout-extensions` enum value covers MODERN `@shopify/ui-extensions` `<s-*>` web components only.

For the legacy SDK: use the `post-purchase-extension` skill and validate with `tsc --noEmit`.

## Instructions

### 1 — Initialize

Call `learn_shopify_api` with the target `api` surface. Consult the [API Surfaces](#api-surfaces) appendix below to confirm the correct `api` value. Extract the returned `conversationId` — pass it to every subsequent call.

### 2 — Route

Determine which tool answers the question: doc search, schema introspection, extension targets, or full page fetch. Consult the [Tools Reference](#tools-reference) below for parameters and gotchas.

### 3 — Use

Call the appropriate tool(s). If switching API surfaces mid-conversation, call `learn_shopify_api` again with the existing `conversationId` and the new `api`.

### 4 — Validate

Before committing any generated code:
- `<s-*>` component markup → `validate_component_codeblocks` (mandatory)
- GraphQL queries/mutations → `validate_graphql_codeblocks` (mandatory)
- Liquid/theme files → `validate_theme` (mandatory)

### 5 — Fix and re-validate

If validation fails, fix errors and re-validate. Increment `revision` on the same `artifactId` to track iterations. If validation fails twice on the same artifact, stop and surface the error to the user.

---

## API Surfaces

All 15 valid values for the `api` param on `learn_shopify_api`:

| `api` value | Description |
|---|---|
| `admin` | Admin GraphQL API (orders, products, metafields) |
| `admin-execution` | Admin API execution surface (Shopify-internal — present in the `learn_shopify_api` enum but NOT in the GraphQL validator enum) |
| `storefront-graphql` | Storefront API (custom storefronts, cart ops) |
| `partner` | Partner API (dashboard data, apps, referrals) |
| `customer` | Customer Account API (orders, payment methods, addresses) |
| `payments-apps` | Payments Apps API (payment provider integrations) |
| `functions` | Shopify Functions (discounts, delivery, cart transforms) |
| `polaris-app-home` | App Home UI (`<s-*>` web components in admin iframe) |
| `polaris-admin-extensions` | Admin action/block extensions |
| `polaris-checkout-extensions` | Modern checkout web-component extensions (`@shopify/ui-extensions`, `<s-*>`). Does NOT cover `@shopify/post-purchase-ui-extensions-react`. |
| `polaris-customer-account-extensions` | Customer account page extensions |
| `pos-ui` | Point of sale UI extensions |
| `hydrogen` | Hydrogen framework |
| `liquid` | Liquid templates |
| `custom-data` | Metafields and metaobjects |

> **Note:** `validate_component_codeblocks` accepts one additional value — `storefront-web-components` — that is NOT valid for `learn_shopify_api`. See the validator's section below.

## Tools Reference

> **Tool availability varies by MCP server build.** Some installations register only a subset (typically: `learn_shopify_api`, `search_docs_chunks`, `validate_component_codeblocks`, `validate_graphql_codeblocks`, `validate_theme`). If a tool below is not callable in your environment, fall back to `search_docs_chunks`.

### `learn_shopify_api`

**Purpose:** Load API overview and get a `conversationId`. Must be called before all other tools.

| Param | Type | Required | Notes |
|---|---|---|---|
| `api` | enum (15 values above) | Yes | Target surface |
| `model` | string | No (always provide) | Telemetry. Schema marks not-required, but the description says "ALWAYS provide". Pass the current model name; pass `'none'` if unknown. |
| `conversationId` | string (UUID) | No | Pass existing ID when switching surfaces mid-conversation. Omit on first call — a new ID is generated and returned. |

**Returns:** `conversationId` (UUID) — required by every subsequent tool call.

**Gotchas:**
- Call again (with same `conversationId`) when switching API surfaces. This loads new context without losing conversation state.
- The response includes a component/API index for the surface — use it to guide subsequent `search_docs_chunks` queries.

---

### `search_docs_chunks`

**Purpose:** Semantic search over shopify.dev documentation. Returns relevant doc chunks with URLs.

| Param | Type | Required | Notes |
|---|---|---|---|
| `conversationId` | string | Yes | From `learn_shopify_api` |
| `prompt` | string | Yes | Natural language search query |
| `api_name` | string | No | Filter results to a specific API surface (use the same value as `api` in `learn_shopify_api`) |
| `max_num_results` | number | No | Limit result count. Omit on first call; use when trimming for context-window constraints. |

**Gotchas:**
- Prefer this over `fetch_full_docs` for targeted lookups.
- For `storefront-graphql`, this is the only reliable doc tool — `introspect_graphql_schema` and `fetch_full_docs` are restricted.

---

### `fetch_full_docs`

**Purpose:** Fetch complete documentation pages by path. Use when you need full property/slot/event details from a page found via `search_docs_chunks`.

| Param | Type | Required | Notes |
|---|---|---|---|
| `conversationId` | string | Yes | From `learn_shopify_api` |
| `paths` | string[] | Yes | Doc paths relative to site root, e.g. `["/docs/api/app-home"]` |

**Gotchas:**
- The `learn_shopify_api` response labels `fetch_full_docs` as DEPRECATED for some surfaces, but where present the tool still works. Prefer `search_docs_chunks`; fall back to `fetch_full_docs` for complete property/slot/event docs.
- For `storefront-graphql`, this tool is restricted — use `search_docs_chunks` instead.
- May not be registered in all MCP server builds.

---

### `validate_component_codeblocks`

**Purpose:** Validate `<s-*>` web component markup against Shopify's schema. Catches hallucinated components, props, and prop values.

| Param | Type | Required | Notes |
|---|---|---|---|
| `conversationId` | string | Yes | From `learn_shopify_api` |
| `api` | enum | Yes | One of: `polaris-app-home`, `polaris-admin-extensions`, `polaris-checkout-extensions`, `polaris-customer-account-extensions`, `pos-ui`, `hydrogen`, `storefront-web-components` (7 values) |
| `code` | array of `{ content: string, artifactId?: string, revision?: number }` | Yes | Code blocks. `content` is required per item. **Param key is `code`** (not `codeblocks`). |
| `extensionTarget` | string | No* | **Required for extension surfaces:** `polaris-admin-extensions`, `polaris-checkout-extensions`, `polaris-customer-account-extensions`, `pos-ui`. Determines which components/APIs are available. Where `learn_extension_target_types` is registered, use it to discover valid targets. |

**Input format:** Wrap code in a function — JS logic outside `return`, components inside `return`:

```js
const Example = () => {
  const [value, setValue] = useState('');

  return (
    <s-page heading="Example">
      <s-section>
        <s-text-field label="Name" value={value} />
      </s-section>
    </s-page>
  );
};
```

Raw HTML also works, but the function wrapper is recommended.

**Gotchas:**
- The param is `code` (array), not `codeblocks` — opposite naming from `validate_graphql_codeblocks`.
- Mandatory after generating ANY `<s-*>` markup — never skip, even for small snippets.
- For `polaris-checkout-extensions`, pass the specific `extensionTarget` (e.g. `purchase.checkout.block.render`) to get accurate validation.
- The validator does **not** type App Bridge web components (`<s-app-window>`, `<s-app-nav>`) as JSX intrinsic elements — they will fail validation in TSX even though they're real components. Use raw HTML, the App Bridge React wrappers (`<TitleBar>`, `<NavMenu>`), or a JSX type augmentation.

---

### GraphQL API enum

**IMPORTANT — this enum differs from `learn_shopify_api`.**

`validate_graphql_codeblocks` and `introspect_graphql_schema` share an expanded 18-value enum where `functions` splits into 13 specific subtypes. **`admin-execution` is NOT in this enum** — even though it's valid for `learn_shopify_api`.

| Value | Description |
|---|---|
| `admin` | Admin GraphQL API |
| `storefront-graphql` | Storefront API |
| `partner` | Partner API |
| `customer` | Customer Account API |
| `payments-apps` | Payments Apps API |
| `functions_cart_checkout_validation` | Cart and Checkout Validation Function inputs |
| `functions_cart_transform` | Cart Transform Function inputs |
| `functions_delivery_customization` | Delivery Customization Function inputs |
| `functions_discount` | Discount Function inputs |
| `functions_discounts_allocator` | Discounts Allocator Function inputs |
| `functions_fulfillment_constraints` | Fulfillment Constraints Function inputs |
| `functions_local_pickup_delivery_option_generator` | Local Pickup Delivery Option Generator inputs |
| `functions_order_discounts` | Order Discounts Function inputs |
| `functions_order_routing_location_rule` | Order Routing Location Rule inputs |
| `functions_payment_customization` | Payment Customization Function inputs |
| `functions_pickup_point_delivery_option_generator` | Pickup Point Delivery Option Generator inputs |
| `functions_product_discounts` | Product Discounts Function inputs |
| `functions_shipping_discounts` | Shipping Discounts Function inputs |

---

### `validate_graphql_codeblocks`

**Purpose:** Validate GraphQL queries/mutations against the Shopify schema. Catches hallucinated fields and operations.

| Param | Type | Required | Notes |
|---|---|---|---|
| `conversationId` | string | Yes | From `learn_shopify_api` |
| `codeblocks` | array of `{ content: string, artifactId?: string, revision?: number }` | Yes | Each `content` is raw GraphQL (no markdown backticks). **Param key is `codeblocks`** (not `code`). |
| `api` | enum | No | Defaults to `admin`. See [GraphQL API enum](#graphql-api-enum). |

**Gotchas:**
- The param is `codeblocks` (array), not `code` — opposite naming from `validate_component_codeblocks`.
- Content must be raw GraphQL, not wrapped in markdown code fences.
- For Functions, use the specific `functions_*` subtype from the [GraphQL API enum](#graphql-api-enum), not `functions`.

---

### `introspect_graphql_schema`

**Purpose:** Explore GraphQL schema — find fields, types, queries, mutations, and required scopes.

| Param | Type | Required | Notes |
|---|---|---|---|
| `conversationId` | string | Yes | From `learn_shopify_api` |
| `query` | string | Yes | Simple search term (e.g. `product`, `discountProduct`, `capture`). One concept at a time. |
| `api` | enum | No | Defaults to `admin`. Same expanded enum as `validate_graphql_codeblocks` — see [GraphQL API enum](#graphql-api-enum). |
| `filter` | string[] | No | Filter results: `all` (default), `types`, `queries`, `mutations`. Pass as array, e.g. `["queries", "mutations"]`. |

**Fallback strategy** (confirmed accurate):
1. Start with the most specific term from the request.
2. If no results, try broader terms or individual words (e.g. `captureSession` → try `capture`).
3. For list operations, try `all`, `list`, or the plural object name.
4. For mutations, try the action verb: `create`, `update`, `delete`.

**Gotchas:**
- Uses the same expanded `api` enum as `validate_graphql_codeblocks` — `functions` splits into 13 subtypes.
- For `storefront-graphql`, this tool is restricted — use `search_docs_chunks` instead.
- May not be registered in all MCP server builds.

---

### `learn_extension_target_types`

**Purpose:** Get type declarations for components and APIs available within a specific extension target.

| Param | Type | Required | Notes |
|---|---|---|---|
| `conversationId` | string | Yes | From `learn_shopify_api` |
| `api` | enum | Yes | The surface |
| `extension_target` | string | Yes | The specific extension target (e.g. `purchase.checkout.block.render`) |

**Supported surfaces:**
- `polaris-admin-extensions`
- `polaris-checkout-extensions`
- `polaris-customer-account-extensions`
- `pos-ui`

**Not supported:**
- `polaris-app-home` — not an extension surface.

**May not be registered in all MCP server builds.** When unavailable, look up valid extension targets via `search_docs_chunks` instead.

---

### `validate_theme`

**Purpose:** Validate Liquid and theme files (JSON locales, config, templates, JS, CSS, SVG).

| Param | Type | Required | Notes |
|---|---|---|---|
| `conversationId` | string | Yes | From `learn_shopify_api` |
| `absoluteThemePath` | string | Yes | Absolute path to theme directory |
| `filesCreatedOrUpdated` | array of `{ path: string, artifactId?: string, revision?: number }` | Yes | `path` is relative to the theme root |

## Validation Reference

### Required params per surface for `validate_component_codeblocks`

| Surface | `api` | `extensionTarget` required? |
|---|---|---|
| `polaris-app-home` | `polaris-app-home` | No |
| `polaris-admin-extensions` | `polaris-admin-extensions` | Yes |
| `polaris-checkout-extensions` | `polaris-checkout-extensions` | Yes |
| `polaris-customer-account-extensions` | `polaris-customer-account-extensions` | Yes |
| `pos-ui` | `pos-ui` | Yes |
| `hydrogen` | `hydrogen` | No |
| `storefront-web-components` | `storefront-web-components` | No |

### Artifact tracking

Both `validate_component_codeblocks` and `validate_graphql_codeblocks` support iterative tracking:
- **`artifactId`** — Stable ID for the code artifact. Omit on first validation (the tool generates one). Reuse the returned ID on subsequent validations of the same artifact.
- **`revision`** — Starts at 1. Increment on each re-validation of the same `artifactId`. Tracks validation retries vs. new validations.
