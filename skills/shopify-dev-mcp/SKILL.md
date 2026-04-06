---
description: "Routes Shopify Dev MCP tools for API lookups, GraphQL doc search, and code validation. Use when writing/modifying GraphQL, calling Shopify APIs, or validating <s-*> markup. Not for pure frontend/CSS work."
model: opus
allowed-tools: mcp__shopify-dev-mcp__*
---

# Shopify Dev MCP

Route MCP tool calls through the appropriate tools below — these are standard lookups, not deep reasoning tasks.

## Workflow

Follow this sequence every time you interact with Shopify Dev MCP tools.

1. **Reference** — Read `references/index.md` (relative to this skill directory) for tool parameters, API enums, and valid input formats. Use to confirm the correct `api` surface before initializing.
2. **Initialize** — Call `learn_shopify_api` with the target `api` surface. Extract the returned `conversationId`. Pass it to every subsequent call.
3. **Route** — Determine which tool answers the question: doc search, schema introspection, extension targets, or full page fetch.
4. **Use** — Call the appropriate tool(s). If switching API surfaces mid-conversation, call `learn_shopify_api` again with the existing `conversationId` and the new `api`.
5. **Validate** — Before committing any generated code:
   - `<s-*>` component markup → `validate_component_codeblocks` (mandatory)
   - GraphQL queries/mutations → `validate_graphql_codeblocks` (mandatory)
   - Liquid/theme files → `validate_theme` (mandatory)
6. **Fix & re-validate** — If validation fails, fix errors and re-validate. Increment `revision` on the same `artifactId` to track iterations.


## When to Validate

| Generated code contains | Tool | Required `api` param |
|---|---|---|
| `<s-*>` web components | `validate_component_codeblocks` | Match the surface (e.g. `polaris-app-home`) |
| GraphQL query/mutation | `validate_graphql_codeblocks` | Match the GraphQL API (e.g. `admin`) |
| Liquid / theme files | `validate_theme` | N/A (uses `absoluteThemePath`) |


## Project Surfaces

This project (Oak Post Purchase) uses three API surfaces:

### `polaris-app-home` — Admin App Home
- React SPA rendered in Shopify Admin iframe
- Uses `<s-*>` web components (Polaris via CDN)
- Validate all markup with `validate_component_codeblocks` (no `extensionTarget` needed)
- `learn_extension_target_types` does NOT work for this surface

### `admin` — Admin GraphQL API
- Orders, products, metafields, shop data
- Validate queries with `validate_graphql_codeblocks` (`api: "admin"`)
- Introspect schema with `introspect_graphql_schema` (`api: "admin"`)

### `polaris-checkout-extensions` — Post-Purchase Checkout Extension
- Shopify checkout sandbox for post-purchase upsell UI
- Uses `<s-*>` web components scoped to checkout context
- Validate markup with `validate_component_codeblocks` — **must pass `extensionTarget`** (e.g. `purchase.checkout.block.render`, `purchase.post-purchase.render`)
- Use `learn_extension_target_types` to discover available targets and their component/API surface
- Components and APIs differ per extension target — always check before building
