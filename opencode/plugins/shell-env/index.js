import { createShellEnv } from "./core.js";

export default {
  id: "agentchatdeck-shell-env",
  async setup(ctx) {
    return createShellEnv(ctx).install();
  },
};
