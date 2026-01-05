This is a [LlamaIndex](https://www.llamaindex.ai/) project bootstrapped with [`create-llama`](https://github.com/run-llama/LlamaIndexTS/tree/main/packages/create-llama).

## Getting Started

First, install the dependencies:

```
npm install
```

Then check the parameters that have been pre-configured in the `.env` file in this directory.
Make sure you have set the `DEEPSEEK_API_KEY` for the LLM (or `OPENAI_API_KEY` as a fallback).

Second, generate the embeddings of the example documents in the `./data` directory:

```
npm run generate
```

Third, run the development server:

```
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the chat UI.

## Configure LLM and Embedding Model

This project uses DeepSeek for the LLM and BAAI (bge-large-en-v1.5) for embeddings. You can configure these in the [settings file](src/app/settings.ts) and [.env file](.env).

The BAAI embedding model runs locally and doesn't require an API key, making it a cost-effective solution for generating embeddings.

## Use Case

We have prepared an [example workflow](./src/app/workflow.ts) for the agentic RAG use case, where you can ask questions about the example documents in the [./data](./data) directory.

You can start by sending an request on the [chat UI](http://localhost:3000) or you can test the `/api/chat` endpoint with the following curl request:

```shell
curl --location 'localhost:3000/api/chat' \
--header 'Content-Type: application/json' \
--data '{ "messages": [{ "role": "user", "content": "What standards for a letter exist?" }] }'
```

## Eject Mode

If you want to fully customize the server UI and routes, you can use `npm eject`. It will create a normal Next.js project with the same functionality as @llamaindex/server.

```bash
npm run eject
```

## Learn More

To learn more about LlamaIndex, take a look at the following resources:

- [LlamaIndex Documentation](https://docs.llamaindex.ai) - learn about LlamaIndex (Python features).
- [LlamaIndexTS Documentation](https://ts.llamaindex.ai/docs/llamaindex) - learn about LlamaIndex (Typescript features).
- [Agent Workflows Introduction](https://ts.llamaindex.ai/docs/llamaindex/modules/agent_workflow) - learn about LlamaIndexTS Agent Workflows.

You can check out [the LlamaIndexTS GitHub repository](https://github.com/run-llama/LlamaIndexTS) - your feedback and contributions are welcome!
