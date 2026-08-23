import { createBridge } from "./core.js";

export default {
  id: "agentchatdeck-claude-rules",
  async setup(ctx) {
    return createBridge(ctx).install();
  },
};
