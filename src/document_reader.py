import os
import re
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

[citation:section-name]

Where:
- [citation:] is the required format for all citations
- `section-name` is the section name from the document (e.g., "major-categories", "material-types", etc.)

Example:
```
Building materials fall under the Building category [citation:major-categories].
Steel I-beams use ferrous metal with code 01 [citation:material-types].
Standard commercial quality has code 06 [citation:quality-grades].
```

## Requirements:
1. Include citations for every fact from the context
2. Place citations immediately after the information they support
3. Use meaningful section names instead of node IDs
4. REMINDER: This tool should only be used AFTER the read_code_generation_file tool has been called for code generation requests. The system monitors actual tool calls, not just claims.
"""


class SectionCitationProcessor:
    """
    Add meaningful section-based citation IDs to nodes based on content
    """
    
    def __init__(self):
        self.section_counter = {}
    
    def get_section_citation_id(self, text: str) -> str:
        """Generate a meaningful citation ID based on content"""
        text_lower = text.lower()
        
        # Check for major sections
        if "major category" in text_lower or "major categories" in text_lower:
            return "major-categories"
        elif "subcategory" in text_lower or "subcategories" in text_lower:
            return "subcategories"
        elif "specific type" in text_lower or "specific types" in text_lower:
            return "specific-types"
        elif "material type" in text_lower or "material types" in text_lower:
            return "material-types"
        elif "quality grade" in text_lower or "quality grades" in text_lower:
            return "quality-grades"
        elif "size category" in text_lower or "size categories" in text_lower:
            return "size-categories"
        elif "suffix format" in text_lower or "date encoding" in text_lower:
            return "date-format"
        elif "code examples" in text_lower:
            return "code-examples"
        elif "best practices" in text_lower:
            return "best-practices"
        elif "quick reference" in text_lower or "reference summary" in text_lower:
            return "quick-reference"
        else:
            # For other content, use a generic approach
            if "code" in text_lower and "structure" in text_lower:
                return "code-structure"
            elif "prefix" in text_lower:
                return "prefix-structure"
            elif "core" in text_lower:
                return "core-structure"
            else:
                return "general-info"
    
    def process_nodes(self, nodes: List[NodeWithScore]) -> List[NodeWithScore]:
        """Process nodes to add section-based citation IDs"""
        for node in nodes:
            section_id = self.get_section_citation_id(node.text)
            node.metadata["citation_id"] = section_id
        return nodes


class AgentCitationSynthesizer(Accumulate):
    """
    Custom synthesizer for agent workflow that handles citations properly
    """
    
    def __init__(self, **kwargs):
        text_qa_template = kwargs.pop("text_qa_template", None)
        if text_qa_template is None:
            text_qa_template = PromptTemplate(template=AGENT_CITATION_PROMPT)
            
            # Log the document reader citation prompt for debugging
            print("\n" + "="*80)
            print("📚 DOCUMENT READER CITATION PROMPT START")
            print("="*80)
            print(AGENT_CITATION_PROMPT)
            print("="*80)
            print("🏁 DOCUMENT READER CITATION PROMPT END")
            print("="*80 + "\n")
            
            # Also write to log file
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open("llm_prompts.log", "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] DOCUMENT READER CITATION PROMPT:\n")
                f.write(f"{'-'*60}\n")
                f.write(f"{AGENT_CITATION_PROMPT}\n")
                f.write(f"{'-'*60}\n\n")
            
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
        node_parser = SentenceSplitter(chunk_size=1000, chunk_overlap=100)
        nodes = node_parser.get_nodes_from_documents([document])
        
        # Process nodes to add section-based citation IDs
        section_processor = SectionCitationProcessor()
        nodes = section_processor.process_nodes(nodes)
        
        # Create a simple in-memory vector store
        vector_store = SimpleVectorStore()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Create index from nodes
        index = VectorStoreIndex(nodes, storage_context=storage_context)
        
        # Create query engine with custom citation synthesizer
        query_engine = index.as_query_engine(
            response_synthesizer=AgentCitationSynthesizer(),
            node_postprocessors=[]
        )
        
        # Create tool
        tool = QueryEngineTool.from_defaults(
            query_engine=query_engine,
            name=f"read_{os.path.basename(file_path).replace('.', '_')}",
            description=f"Use this tool to read the {os.path.basename(file_path)} file. This contains information that can be referenced with citations in the format [citation:section-name]."
        )
        
        return tool
        
    except Exception as e:
        raise RuntimeError(f"Error creating document reader tool for {file_path}: {str(e)}")