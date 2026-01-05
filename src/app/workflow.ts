import { agent } from "@llamaindex/workflow";
import { Settings } from "llamaindex";
import { getIndex } from "./data";

export const workflowFactory = async (reqBody: any) => {
  const index = await getIndex(reqBody?.data);

  const queryEngineTool = index.queryTool({
    metadata: {
      name: "query_document",
      description: `Use this tool to search for information about USPS physical standards.
      When a user asks about dimensional requirements, weight limits, or mailability criteria for letters, cards, flats, or parcels, use this tool to retrieve the relevant information from the USPS Domestic Mail Manual.`,
    },
    includeSourceNodes: true,
  });

  // Add custom error handling to the query tool
  const originalCall = queryEngineTool.call.bind(queryEngineTool);
  queryEngineTool.call = async (input: any) => {
    try {
      console.log("Query tool called with input:", JSON.stringify(input, null, 2));
      const result = await originalCall(input);
      console.log("Query tool result type:", typeof result);
      console.log("Query tool result:", JSON.stringify(result, null, 2));
      
      // Ensure result is properly serialized
      if (result === undefined || result === null) {
        console.log("Result is undefined or null, returning error response");
        return "No results found in the document. Please try a different query.";
      }
      
      // Check if result has content property
      const resultObj = result as any;
      if (resultObj && typeof resultObj === 'object' && resultObj.content !== undefined) {
        console.log("Found content in result, type:", typeof resultObj.content);
        console.log("Content value:", resultObj.content);
        
        // Return just the content as a string, which should be serializable
        return resultObj.content;
      }
      
      // If result is already a string or primitive, return it directly
      if (typeof result === 'string' || typeof result === 'number' || typeof result === 'boolean') {
        console.log("Result is a primitive, returning directly:", result);
        return result;
      }
      
      // If we get here, try to stringify the result
      console.log("Attempting to stringify result");
      return JSON.stringify(result);
    } catch (error) {
      console.error("Query tool error:", error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      return `Error querying document: ${errorMessage}`;
    }
  };
  
  // Add logging to debug query tool
  console.log("Query tool created with error handling:", queryEngineTool);

  return agent({
    tools: [queryEngineTool],
    llm: Settings.llm as any,
    verbose: true, // Enable verbose logging for the agent
    systemPrompt: `You are a helpful assistant that provides information about USPS physical standards for mail.
    When a user asks a question, use the query_document tool to retrieve relevant information from the knowledge base.
    After retrieving information, provide a clear and concise answer based on the retrieved content.
    Always cite the specific standards or requirements from the document.`,
  });
};
