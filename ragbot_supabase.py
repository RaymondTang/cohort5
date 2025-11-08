# ==============================================================================
# RAG-based News Agent with PydanticAI and LlamaIndex
# ==============================================================================
# This script demonstrates how to build a Retrieval-Augmented Generation (RAG)
# system that combines PydanticAI agents with LlamaIndex for document retrieval.
# The agent can search through BBC news articles to answer questions about
# current events and news topics.

# Core PydanticAI imports for building intelligent agents
from pydantic_ai import Agent, RunContext

# Vector database and retrieval components
from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding  # Text embeddings
from llama_index.vector_stores.supabase import SupabaseVectorStore  # Supabase integration
from llama_index.core.retrievers import BaseRetriever  # Base retriever interface

# Standard library and utility imports
from typing import List
from dotenv import load_dotenv  # Environment variable management
import os
from dataclasses import dataclass
from langfuse import get_client
# Load environment variables from .env file
load_dotenv()

langfuse = get_client()

# Verify connection
if langfuse.auth_check():
    Agent.instrument_all()
else:
    print("Authentication failed. Please check your credentials and host.")

# ==============================================================================
# Supabase Configuration
# ==============================================================================
SUPABASE_POSTGRES_URI = os.getenv("SUPABASE_POSTGRES_URI")
SUPABASE_COLLECTION = os.getenv("SUPABASE_COLLECTION", "bbc_news")
SUPABASE_DIMENSION = int(os.getenv("SUPABASE_DIMENSION", "1024"))

if not SUPABASE_POSTGRES_URI:
    raise ValueError("SUPABASE_POSTGRES_URI environment variable is required.")

# ==============================================================================
# Vector Database and Embedding Setup
# ==============================================================================
# Configure embedding model for converting text to vectors
embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-m3",  # Efficient English embedding model
    device="mps",  # Use Metal Performance Shaders on Mac (change to "cuda" for GPU)
    embed_batch_size=10,  # Process embeddings in batches
)

# Global LlamaIndex settings for document processing
Settings.embed_model = embed_model
Settings.chunk_size = 512  # Size of text chunks for processing
Settings.chunk_overlap = 50  # Overlap between chunks to maintain context

# ==============================================================================
# Vector Store and Retriever Initialization
# ==============================================================================
vector_store = SupabaseVectorStore(
    postgres_connection_string=SUPABASE_POSTGRES_URI,
    collection_name=SUPABASE_COLLECTION,
    dimension=SUPABASE_DIMENSION,
)

try:
    # Create vector index from existing Supabase collection
    index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
except Exception as exc:
    raise RuntimeError(
        f"Failed to load Supabase collection '{SUPABASE_COLLECTION}'. "
        "Ensure doc_ingestion_supabase has been run at least once."
    ) from exc

# Create retriever to search for relevant documents
retriever = index.as_retriever(similarity_top_k=5)  # Return top 5 most similar documents

# ==============================================================================
# Agent Dependencies Definition
# ==============================================================================
@dataclass
class RagDeps:
    """Dependencies for the RAG (Retrieval-Augmented Generation) agents.
    
    Attributes:
        retriever: A LlamaIndex BaseRetriever instance used to search through
                  the BBC News database for relevant articles and information.
    """
    retriever: BaseRetriever

# ==============================================================================
# PydanticAI Agent Configuration
# ==============================================================================
# Create a specialized news agent with retrieval capabilities
bbc_agent = Agent(
    model='openrouter:google/gemini-2.5-flash-lite',  # Use the configured Gemini model
    deps_type=RagDeps,  # Specify the dependency type for type safety
    # Define the agent's role and behavior
    system_prompt=(
        'Please answer everything in Traditional Chinese.'
        'You are a news assistant that helps users find relevant news information. '
        'When users ask questions about current events, news, politics, sports, technology, '
        'business, entertainment, or any topic that would require up-to-date information, '
        'use the retriever tool to search for relevant news articles first. '
        'Base your response on the retrieved information and cite the sources when possible. '
        'If the question is not related to news or current events (like general knowledge, '
        'personal advice, or simple calculations), answer directly without using the retriever. '
    ),
)

# ==============================================================================
# Tool Function Definition
# ==============================================================================
@bbc_agent.tool
async def get_bbc_news(ctx: RunContext[RagDeps], query: str) -> List[str]:
    """Search for relevant BBC news articles based on a query.
    
    Use this tool when users ask about current events, news, politics, economics,
    international relations, business developments, or any topic that would benefit
    from recent news information. This tool searches through a database of BBC news
    articles to find the most relevant content.
    
    Args:
        query: A search query describing the news topic or information needed.
               Should be specific and use relevant keywords but keep it as full sentence.
               (e.g., "Latest news about China and US trade tariff",
               "What is the latest developement about Brexit negotiations", etc.). 
    
    Returns:
        List[str]: A list of relevant news article excerpts or summaries that match
                  the search query. Each item contains text content from BBC news articles.
    
    Examples of when to use this tool:
    - "What's the latest on China-US trade relations?"
    - "Tell me about recent climate change policies"
    - "What happened in the UK elections?"
    - "Any news about technology companies and AI regulation?"
    """
    # Use the retriever to find relevant documents based on the query
    results = ctx.deps.retriever.retrieve(query)
    
    # Extract text content from retrieved documents
    return [result.text for result in results]

# ==============================================================================
# Agent Execution Example
# ==============================================================================
# Create dependencies instance with the configured retriever
deps = RagDeps(retriever=retriever)

# Run the agent with a sample query about trade relations
result_sync = bbc_agent.run_sync('Can you tell me the news about trading tariff between China and US?', deps=deps)

# Display the agent's response
print(result_sync.output)
