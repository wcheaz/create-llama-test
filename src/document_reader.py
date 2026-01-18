import os
from typing import List, Optional

from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.query_engine.retriever_query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import Accumulate
from llama_index.core.schema import NodeWithScore
from llama_index.core.tools.query_engine import QueryEngineTool
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core.storage import StorageContext
from llama_index.core.indices import VectorStoreIndex
from llama_index.core.prompts import PromptTemplate

from src.citation import NodeCitationProcessor


# Custom prompt template for agent workflow citation
AGENT_CITATION_PROMPT = """
Context information is below.
------------------
{context_str}
------------------
The context contains multiple text chunks, each with a citation_id. Use these citation_ids for citations.

Answer the following query with citations:
------------------
{query_str}
------------------

## Citation format

[citation:id]

Where:
- [citation:] is the required format for all citations
- `id` is the citation_id from the context

Example:
```
Medical equipment would fall under Technology category [citation:abc123].
Surgical instruments are considered technical items [citation:def456].
```

## Requirements:
1. Include citations for every fact from the context
2. Place citations immediately after the information they support
3. Don't mix up citation_ids
"""


class AgentCitationSynthesizer(Accumulate):
    """
    Custom synthesizer for agent workflow that handles citations properly
    """
    
    def __init__(self, **kwargs):
        text_qa_template = kwargs.pop("text_qa_template", None)
        if text_qa_template is None:
            text_qa_template = PromptTemplate(template=AGENT_CITATION_PROMPT)
        super().__init__(text_qa_template=text_qa_template, **kwargs)


def create_document_reader_tool(file_path: str) -> QueryEngineTool:
    """
    Create a query engine tool for reading a document with citation support.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        A QueryEngineTool with citation support enabled
    """
    try:
        # Read the document
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create a document
        document = Document(text=content, metadata={"filename": os.path.basename(file_path)})
        
        # Create nodes with larger chunks for better context
        node_parser = SentenceSplitter(chunk_size=800, chunk_overlap=80)
        nodes = node_parser.get_nodes_from_documents([document])
        
        # Add citation IDs to nodes
        for node in nodes:
            node.metadata["citation_id"] = node.node_id
        
        # Create a simple in-memory vector store
        vector_store = SimpleVectorStore()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Create index from nodes
        index = VectorStoreIndex(nodes, storage_context=storage_context)
        
        # Create query engine with custom citation synthesizer
        query_engine = index.as_query_engine(
            response_synthesizer=AgentCitationSynthesizer(),
            node_postprocessors=[NodeCitationProcessor()]
        )
        
        # Create tool
        tool = QueryEngineTool.from_defaults(
            query_engine=query_engine,
            name=f"read_{os.path.basename(file_path).replace('.', '_')}",
            description=f"Use this tool to read the {os.path.basename(file_path)} file. This contains information that can be referenced with citations in the format [citation:id]."
        )
        
        return tool
        
    except Exception as e:
        raise RuntimeError(f"Error creating document reader tool for {file_path}: {str(e)}")