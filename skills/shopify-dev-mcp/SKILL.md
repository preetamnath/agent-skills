---
name: shopify-dev-mcp
description: "Routes Shopify Dev MCP calls for schema introspection, doc search, and code validation of GraphQL + <s-*> markup. Use when writing/editing GraphQL against Shopify Admin/Storefront/Customer APIs, generating or validating <s-*> web components, touching checkout/admin/customer-account extension UI, editing shopify.app.toml, or looking up a Shopify API field, type, or extension target."
model: opus
allowed-tools: mcp__shopify-dev-mcp__*
---

# Shopify Dev MCP

Route MCP tool calls through the appropriate tools — standard lookups, not deep reasoning tasks.

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

**Returns:** `conversationId` (UUID) — required by every subsequent tool call.

**Gotchas:**
- Call again (with same `conversationId`) when switching API surfaces. This loads new context without losing conversation state.
- The response includes a component/API index for the surface — use it to guide subsequent `search_docs_chunks` queries.

### `search_docs_chunks`

**Purpose:** Semantic search over shopify.dev documentation. Returns relevant doc chunks with URLs.

**Gotchas:**
- Prefer this over `fetch_full_docs` for targeted lookups.
- For `storefront-graphql`, this is the only reliable doc tool — `introspect_graphql_schema` and `fetch_full_docs` are restricted.

### `fetch_full_docs`

**Purpose:** Fetch complete documentation pages by path. Use when you need full property/slot/event details from a page found via `search_docs_chunks`.

**Gotchas:**
- The `learn_shopify_api` response labels `fetch_full_docs` as DEPRECATED for some surfaces, but the tool works. Prefer `search_docs_chunks`; fall back to `fetch_full_docs` for complete property/slot/event docs.
- For `storefront-graphql`, this tool is restricted — use `search_docs_chunks` instead.

### `validate_component_codeblocks`

**Purpose:** Validate `<s-*>` web component markup against Shopify's schema. Catches hallucinated components, props, and prop values.

**Gotchas:**
- The param is `code` (array), not `codeblocks` — opposite naming from `validate_graphql_codeblocks`.
- Wrap code in a function with JS logic outside `return` and components inside `return`; raw HTML also works but the function wrapper is recommended.
- Mandatory after generating ANY `<s-*>` markup — never skip, even for small snippets.
- For extension surfaces (`polaris-checkout-extensions`, `polaris-admin-extensions`, `polaris-customer-account-extensions`, `pos-ui`), `extensionTarget` is required — get valid targets via `learn_extension_target_types`.
- For `polaris-checkout-extensions`, pass the specific `extensionTarget` (e.g. `purchase.checkout.block.render`) to get accurate validation.

### GraphQL API enum

**IMPORTANT — this enum differs from `learn_shopify_api`.**

`validate_graphql_codeblocks` and `introspect_graphql_schema` share an expanded enum where `functions` splits into 14 specific subtypes:

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

### `validate_graphql_codeblocks`

**Purpose:** Validate GraphQL queries/mutations against the Shopify schema. Catches hallucinated fields and operations.

**Gotchas:**
- The param is `codeblocks` (array), not `code` — opposite naming from `validate_component_codeblocks`.
- Content must be raw GraphQL, not wrapped in markdown code fences.
- For Functions, use the specific `functions_*` subtype from the [GraphQL API enum](#graphql-api-enum), not `functions`.

### `introspect_graphql_schema`

**Purpose:** Explore GraphQL schema — find fields, types, queries, mutations, and required scopes.

**Fallback strategy** (confirmed accurate):
1. Start with the most specific term from the request
2. If no results, try broader terms or individual words (e.g. `captureSession` → try `capture`)
3. For list operations, try `all`, `list`, or the plural object name
4. For mutations, try the action verb: `create`, `update`, `delete`

**Gotchas:**
- Uses the same expanded `api` enum as `validate_graphql_codeblocks` — `functions` splits into 14 subtypes. See [GraphQL API enum](#graphql-api-enum).
- For `storefront-graphql`, this tool is restricted — use `search_docs_chunks` instead.

### `learn_extension_target_types`

**Purpose:** Get type declarations for components and APIs available within a specific extension target.

**Gotchas:**
- Supported surfaces: `polaris-admin-extensions`, `polaris-checkout-extensions`, `polaris-customer-account-extensions`, `pos-ui`.
- `polaris-app-home` is NOT supported — it is not an extension surface.

### `validate_theme`

**Purpose:** Validate Liquid and theme files (JSON locales, config, templates, JS, CSS, SVG).

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
