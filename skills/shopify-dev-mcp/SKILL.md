---
name: shopify-dev-mcp
description: "Routes Shopify Dev MCP tools for API lookups, GraphQL doc search, and code validation. Use when writing/modifying GraphQL, calling Shopify APIs, or validating <s-*> markup. Not for pure frontend/CSS work."
model: opus
allowed-tools: mcp__shopify-dev-mcp__*
---

# Shopify Dev MCP

Route MCP tool calls through the appropriate tools — standard lookups, not deep reasoning tasks.

## When to use

Writing/modifying GraphQL, calling Shopify APIs, or validating `<s-*>` markup.
Not for pure frontend/CSS work.

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

If validation fails, fix errors and re-validate. Increment `revision` on the same `artifactId` to track iterations. If validation fails twice on the same issue, use the `AskUserQuestion` tool with options: "Try a different approach", "Skip validation and proceed", "Stop and investigate manually". Recommended: "Try a different approach".

## When to Validate

| Generated code contains | Tool | Required `api` param |
|---|---|---|
| `<s-*>` web components | `validate_component_codeblocks` | Match the surface (e.g. `polaris-app-home`) |
| GraphQL query/mutation | `validate_graphql_codeblocks` | Match the GraphQL API (e.g. `admin`) |
| Liquid / theme files | `validate_theme` | N/A (uses `absoluteThemePath`) |

## Rules

- **Always validate.** Never skip validation for generated `<s-*>` markup, GraphQL, or Liquid — even small snippets.
- **Track artifacts.** Reuse `artifactId` and increment `revision` on re-validation.
- **Surface matters.** Use the correct `api` enum value for each surface — they differ between tools.

---

<!-- source: references/shopify-dev-mcp-tools.md -->

## API Surfaces

All 14 valid values for the `api` param on `learn_shopify_api`:

| `api` value | Description |
|---|---|
| `admin` | Admin GraphQL API (orders, products, metafields) |
| `storefront-graphql` | Storefront API (custom storefronts, cart ops) |
| `partner` | Partner API (dashboard data, apps, referrals) |
| `customer` | Customer Account API (orders, payment methods, addresses) |
| `payments-apps` | Payments Apps API (payment provider integrations) |
| `functions` | Shopify Functions (discounts, delivery, cart transforms) |
| `polaris-app-home` | App Home UI (`<s-*>` web components in admin iframe) |
| `polaris-admin-extensions` | Admin action/block extensions |
| `polaris-checkout-extensions` | Checkout/post-purchase UI extensions |
| `polaris-customer-account-extensions` | Customer account page extensions |
| `pos-ui` | Point of sale UI extensions |
| `hydrogen` | Hydrogen framework |
| `liquid` | Liquid templates |
| `custom-data` | Metafields and metaobjects |

## Tools Reference

### `learn_shopify_api`

**Purpose:** Load API overview and get a `conversationId`. Must be called before all other tools.

| Param | Type | Required | Notes |
|---|---|---|---|
| `api` | enum (14 values above) | Yes | Target surface |
| `model` | string | No (recommended) | Pass your current model name (e.g. the model you are running as). Do not hardcode a specific model. |
| `conversationId` | string | No | Pass existing ID when switching surfaces mid-conversation |

**Returns:** `conversationId` (UUID) — required by every subsequent tool call.

**Gotchas:**
- Call again (with same `conversationId`) when switching API surfaces. This loads new context without losing conversation state.
- The response includes a component/API index for the surface — use it to guide subsequent `search_docs_chunks` queries.

### `search_docs_chunks`

**Purpose:** Semantic search over shopify.dev documentation. Returns relevant doc chunks with URLs.

| Param | Type | Required | Notes |
|---|---|---|---|
| `conversationId` | string | Yes | From `learn_shopify_api` |
| `prompt` | string | Yes | Natural language search query |
| `api_name` | string | No | Filter results to a specific API surface (use same value as `api` in `learn_shopify_api`) |
| `max_num_results` | number | No | Limit result count. Omit on first call; use when trimming for context window constraints. |

**Gotchas:**
- Prefer this over `fetch_full_docs` for targeted lookups.
- For `storefront-graphql`, this is the only reliable doc tool — `introspect_graphql_schema` and `fetch_full_docs` are restricted.

### `fetch_full_docs`

**Purpose:** Fetch complete documentation pages by path. Use when you need full property/slot/event details from a page found via `search_docs_chunks`.

| Param | Type | Required | Notes |
|---|---|---|---|
| `conversationId` | string | Yes | From `learn_shopify_api` |
| `paths` | string[] | Yes | Doc paths relative to site root, e.g. `["/docs/api/app-home"]` |

**Gotchas:**
- The `learn_shopify_api` response labels `fetch_full_docs` as DEPRECATED for some surfaces, but the tool works. Prefer `search_docs_chunks`; fall back to `fetch_full_docs` for complete property/slot/event docs.
- For `storefront-graphql`, this tool is restricted — use `search_docs_chunks` instead.

### `validate_component_codeblocks`

**Purpose:** Validate `<s-*>` web component markup against Shopify's schema. Catches hallucinated components, props, and prop values.

| Param | Type | Required | Notes |
|---|---|---|---|
| `conversationId` | string | Yes | From `learn_shopify_api` |
| `api` | enum | Yes | One of: `polaris-app-home`, `polaris-admin-extensions`, `polaris-checkout-extensions`, `polaris-customer-account-extensions`, `pos-ui`, `hydrogen`, `storefront-web-components` |
| `code` | array of objects | Yes | Each object: `{ content: string, artifactId?: string, revision?: number }` |
| `extensionTarget` | string | No* | **Required for extension surfaces:** `polaris-checkout-extensions`, `polaris-admin-extensions`, `polaris-customer-account-extensions`, `pos-ui`. Determines which components/APIs are available. Get valid targets via `learn_extension_target_types`. |
| `artifactId` | | | Stable ID for the code artifact. Omit on first validation (tool generates one). Reuse on re-validation. |
| `revision` | | | Starts at 1. Increment on each re-validation of the same `artifactId`. |

**Input format:** Wrap code in a function. JS logic outside `return`, components inside `return`:

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

Raw HTML also works but the function wrapper is recommended.

**Gotchas:**
- Mandatory after generating ANY `<s-*>` markup — never skip, even for small snippets.
- For `polaris-checkout-extensions`, pass the specific `extensionTarget` (e.g. `purchase.checkout.block.render`) to get accurate validation.

### `validate_graphql_codeblocks`

**Purpose:** Validate GraphQL queries/mutations against the Shopify schema. Catches hallucinated fields and operations.

| Param | Type | Required | Notes |
|---|---|---|---|
| `conversationId` | string | Yes | From `learn_shopify_api` |
| `codeblocks` | array of objects | Yes | Each object: `{ content: string, artifactId?: string, revision?: number }`. Content is raw GraphQL (no markdown backticks). |
| `api` | enum | No | Defaults to `admin`. See expanded enum below. |
| `artifactId` | | | Stable ID. Omit on first validation; reuse on re-validation. |
| `revision` | | | Starts at 1. Increment on each re-validation pass. |

**IMPORTANT — `api` enum differs from `learn_shopify_api`:**

This tool and `introspect_graphql_schema` use a different, expanded enum. The `functions` surface splits into 14 specific subtypes:

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

**Gotchas:**
- The param is `codeblocks` (array), not `code`.
- Content must be raw GraphQL, not wrapped in markdown code fences.
- For Functions, use the specific `functions_*` subtype, not `functions`.

### `introspect_graphql_schema`

**Purpose:** Explore GraphQL schema — find fields, types, queries, mutations, and required scopes.

| Param | Type | Required | Notes |
|---|---|---|---|
| `conversationId` | string | Yes | From `learn_shopify_api` |
| `query` | string | Yes | Simple search term (e.g. `product`, `discountProduct`, `capture`). One concept at a time. |
| `api` | enum | No | Defaults to `admin`. Same expanded enum as `validate_graphql_codeblocks` (see table above). |
| `filter` | string[] | No | Filter results: `all` (default), `types`, `queries`, `mutations`. Pass as array, e.g. `["queries", "mutations"]`. |

**Fallback strategy** (confirmed accurate):
1. Start with the most specific term from the request
2. If no results, try broader terms or individual words (e.g. `captureSession` → try `capture`)
3. For list operations, try `all`, `list`, or the plural object name
4. For mutations, try the action verb: `create`, `update`, `delete`

**Gotchas:**
- Uses the same expanded `api` enum as `validate_graphql_codeblocks` — `functions` splits into 14 subtypes.
- For `storefront-graphql`, this tool is restricted — use `search_docs_chunks` instead.

### `learn_extension_target_types`

**Purpose:** Get type declarations for components and APIs available within a specific extension target.

| Param | Type | Required | Notes |
|---|---|---|---|
| `conversationId` | string | Yes | From `learn_shopify_api` |
| `api` | enum (14 values) | Yes | The surface |
| `extension_target` | string | Yes | The specific extension target (e.g. `purchase.checkout.block.render`) |

**Supported surfaces:**
- `polaris-admin-extensions` — works
- `polaris-checkout-extensions` — works
- `polaris-customer-account-extensions` — works
- `pos-ui` — works

**Not supported:**
- `polaris-app-home` — this tool does not work for App Home (it is not an extension surface)

### `validate_theme`

**Purpose:** Validate Liquid and theme files (JSON locales, config, templates, JS, CSS, SVG).

| Param | Type | Required | Notes |
|---|---|---|---|
| `conversationId` | string | Yes | From `learn_shopify_api` |
| `absoluteThemePath` | string | Yes | Absolute path to theme directory |
| `filesCreatedOrUpdated` | array of objects | Yes | Each: `{ path: string, artifactId?: string, revision?: number }`. Path is relative to theme root. |

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
