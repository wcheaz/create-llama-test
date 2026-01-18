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

from src.citation import NodeCitationProcessor, CitationSynthesizer, enable_citation


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
        
        # Create nodes with sentence splitting for better granularity
        node_parser = SentenceSplitter(chunk_size=200, chunk_overlap=20)
        nodes = node_parser.get_nodes_from_documents([document])
        
        # Create a simple in-memory vector store
        vector_store = SimpleVectorStore()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Create index from nodes
        index = VectorStoreIndex(nodes, storage_context=storage_context)
        
        # Create query engine
        query_engine = index.as_query_engine(
            response_synthesizer=CitationSynthesizer(),
            node_postprocessors=[NodeCitationProcessor()]
        )
        
        # Create tool
        tool = QueryEngineTool.from_defaults(
            query_engine=query_engine,
            name=f"read_{os.path.basename(file_path).replace('.', '_')}",
            description=f"Use this tool to read the {os.path.basename(file_path)} file. This contains information that can be referenced with citations."
        )
        
        # Enable citations
        return enable_citation(tool)
        
    except Exception as e:
        raise RuntimeError(f"Error creating document reader tool for {file_path}: {str(e)}")