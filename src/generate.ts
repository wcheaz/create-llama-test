import { SimpleDirectoryReader } from "@llamaindex/readers/directory";
import "dotenv/config";
import { storageContextFromDefaults, VectorStoreIndex, Settings, SentenceSplitter } from "llamaindex";
import { initSettings } from "./app/settings";

async function generateDatasource() {
  console.log(`Generating storage context...`);
  
  // Ensure embedding model is set consistently
  initSettings();
  
  // Split documents, create embeddings and store them in the storage context
  const storageContext = await storageContextFromDefaults({
    persistDir: "storage", // Path relative to project root when running from project directory
  });
  
  // load documents from current directory into an index
  const reader = new SimpleDirectoryReader();
  const documents = await reader.loadData("data");

  // Use a sentence splitter for better chunking
  const splitter = new SentenceSplitter({
    chunkSize: 512,
    chunkOverlap: 50,
  });

  // Apply transformations to documents before creating index
  const transformedDocuments = await splitter.getNodesFromDocuments(documents);

  await VectorStoreIndex.fromDocuments(transformedDocuments, {
    storageContext,
  });
  console.log("Storage context successfully generated.");
}

(async () => {
  const args = process.argv.slice(2);
  const command = args[0];

  if (command === "ui") {
    console.error("This project doesn't use any custom UI.");
    return;
  } else {
    if (command !== "datasource") {
      console.error(
        `Unrecognized command: ${command}. Generating datasource by default.`,
      );
    }
    await generateDatasource();
  }
})();
