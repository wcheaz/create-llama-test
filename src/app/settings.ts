import { OpenAI, OpenAIEmbedding } from "@llamaindex/openai";
import { Settings } from "llamaindex";

export function initSettings() {
  Settings.llm = new OpenAI({
    model: process.env.MODEL ?? "deepseek-chat",
    apiKey: process.env.DEEPSEEK_API_KEY ?? process.env.OPENAI_API_KEY,
    maxTokens: process.env.LLM_MAX_TOKENS
      ? Number(process.env.LLM_MAX_TOKENS)
      : undefined,
    // Use DeepSeek's API endpoint if DEEPSEEK_API_BASE is provided
    ...(process.env.DEEPSEEK_API_BASE && {
      baseURL: process.env.DEEPSEEK_API_BASE
    }),
  });
  Settings.embedModel = new OpenAIEmbedding({
    model: process.env.EMBEDDING_MODEL ?? "text-embedding-3-large",
    apiKey: process.env.DEEPSEEK_API_KEY ?? process.env.OPENAI_API_KEY,
    dimensions: process.env.EMBEDDING_DIM
      ? parseInt(process.env.EMBEDDING_DIM)
      : undefined,
    // Use DeepSeek's API endpoint if DEEPSEEK_API_BASE is provided
    ...(process.env.DEEPSEEK_API_BASE && {
      baseURL: process.env.DEEPSEEK_API_BASE
    }),
  });
}
