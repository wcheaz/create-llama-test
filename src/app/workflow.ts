import { agent } from "@llamaindex/workflow";
import { Settings } from "llamaindex";
import { getIndex } from "./data";

export const workflowFactory = async (reqBody: any) => {
  const index = await getIndex(reqBody?.data);

  const queryEngineTool = index.queryTool({
    metadata: {
      name: "query_document",
      description: `This tool can retrieve information about USPS physical standards for letters, cards, flats, and parcels, including dimensional requirements, weight limits, and mailability criteria`,
    },
    includeSourceNodes: true,
  });

  // Explicitly pass the configured LLM to the agent
  return agent({
    tools: [queryEngineTool],
    llm: Settings.llm as any  // Type assertion to resolve TypeScript error
  });
};
