import { OpenAI } from "@llamaindex/openai";
import { HuggingFaceEmbedding } from "@llamaindex/huggingface";
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
  
  // Use BAAI embeddings instead of OpenAI embeddings
  Settings.embedModel = new HuggingFaceEmbedding({
    modelType: process.env.EMBEDDING_MODEL ?? "BAAI/bge-large-en-v1.5",
    // Additional configuration options can be added here if needed
    // quantized: true, // Optional: Use quantized model for faster inference
  });
}
