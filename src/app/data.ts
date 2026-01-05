import {
  SimpleDocumentStore,
  storageContextFromDefaults,
  VectorStoreIndex,
  Settings,
} from "llamaindex";
import { initSettings } from "./settings";

export async function getIndex(params?: any) {
  // Ensure settings are initialized with the correct embedding model
  initSettings();
  
  const storageContext = await storageContextFromDefaults({
    persistDir: "storage", // Path relative to project root (where server is started)
  });

  const numberOfDocs = Object.keys(
    (storageContext.docStore as SimpleDocumentStore).toDict(),
  ).length;
  if (numberOfDocs === 0) {
    throw new Error(
      "Index not found. Please run `npm run generate` to generate the embeddings of the documents",
    );
  }

  return await VectorStoreIndex.init({ storageContext });
}
