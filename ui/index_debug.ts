import { LlamaIndexServer } from "@llamaindex/server";

new LlamaIndexServer({
  uiConfig: {
    componentsDir: "components",
    layoutDir: "layout",
    llamaDeploy: { deployment: "chat_debug", workflow: "debug_workflow" },
  },
}).start();