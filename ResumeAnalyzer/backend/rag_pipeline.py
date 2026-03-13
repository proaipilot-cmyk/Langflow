from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from backend.database import resume_collection, OPENROUTER_API_KEY
from dotenv import load_dotenv
import os
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()
logger = logging.getLogger(__name__)


# Initialize embeddings with error handling
try:
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    if not mistral_api_key:
        raise ValueError("MISTRAL_API_KEY environment variable is not set")
    
    embeddings = MistralAIEmbeddings(
        model="mistral-embed",
        api_key=mistral_api_key
    )
    logger.info("Mistral embeddings initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize embeddings: {e}")
    raise RuntimeError(f"Embeddings initialization failed: {e}")

# Initialize MongoDB Vector Store with error handling
try:
    vector_store = MongoDBAtlasVectorSearch(
        collection=resume_collection,
        embedding=embeddings,
        index_name="Resume_Vector"
    )
    logger.info("Vector store initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize vector store: {e}")
    raise RuntimeError(f"Vector store initialization failed: {e}")


# Document ingestion with retry logic
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def ingest_document(documents):
    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        chunks = splitter.split_documents(documents)

        texts = [doc.page_content for doc in chunks]
        metadatas = [doc.metadata for doc in chunks]

        vector_store.add_texts(
            texts=texts,
            metadatas=metadatas
        )
        logger.info(f"Successfully ingested {len(texts)} text chunks")
    except Exception as e:
        logger.error(f"Document ingestion failed: {e}")
        raise


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def build_chain():
    try:
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        logger.info("Retriever initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize retriever: {e}")
        raise RuntimeError(f"Retriever initialization failed: {e}")

    # Use environment variable for API key (removed hardcoded key)
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")
    
    # llm = ChatOpenAI(
    #     model="openai/gpt-oss-20b:free",
    #     base_url="https://openrouter.ai/api/v1",
    #     api_key=openrouter_api_key
    # )
    llm = ChatOpenAI(
            model="meta-llama/llama-3-8b-instruct",
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )

    prompt = ChatPromptTemplate.from_template(
        """You are a resume search assistant.

Use the provided resume context to answer the user's query.

Context:
{context}

Question:
{question}
"""
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    from operator import itemgetter
    
    try:
        rag_chain = (
            {
                "context": itemgetter("input") | retriever | format_docs,
                "question": itemgetter("input"),
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        logger.info("RAG chain built successfully")
        return rag_chain
    except Exception as e:
        logger.error(f"Failed to build RAG chain: {e}")
        raise RuntimeError(f"RAG chain building failed: {e}")