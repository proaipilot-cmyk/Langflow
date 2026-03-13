from fastapi import FastAPI, UploadFile, HTTPException, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.rag_pipeline import ingest_document, build_chain
from langchain_community.document_loaders import PyPDFLoader
import tempfile
import os
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Resume Analyzer RAG API", version="1.0.0")

# Request/Response Models
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    
class SearchResponse(BaseModel):
    answer: str
    sources: Optional[list] = None
    
class UploadResponse(BaseModel):
    status: str
    filename: str
    chunks_ingested: int

# Initialize RAG chain with error handling
try:
    rag_chain = build_chain()
    logger.info("RAG chain initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize RAG chain: {e}")
    rag_chain = None

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Application startup: Resume Analyzer RAG API")
    if rag_chain is None:
        logger.error("WARNING: RAG chain failed to initialize. Some features may not work.")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Application shutdown: Resume Analyzer RAG API")

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "service": "Resume Analyzer RAG API",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/upload", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and ingest a resume PDF file
    
    Args:
        file: PDF file to upload
        
    Returns:
        UploadResponse with upload status and chunk count
    """
    logger.info(f"Upload request received for file: {file.filename}")
    
    # Validate file type
    if not file.filename.endswith(".pdf"):
        logger.warning(f"Invalid file type: {file.filename}")
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed. Please upload a .pdf file."
        )
    
    # Validate file size (max 50MB)
    file_content = await file.read()
    file_size = len(file_content)
    await file.seek(0)  # Reset file pointer
    
    if file_size > 50 * 1024 * 1024:
        logger.warning(f"File too large: {file.filename} ({file_size} bytes)")
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum size is 50MB."
        )
    
    temp_path = None
    try:
        # Use a secure temp file to parse the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(file_content)
            temp_path = temp.name
        
        logger.info(f"Loading PDF: {file.filename}")
        loader = PyPDFLoader(temp_path)
        documents = loader.load()
        
        if not documents:
            logger.warning(f"No content extracted from {file.filename}")
            raise HTTPException(
                status_code=400,
                detail="No text content could be extracted from the PDF."
            )
        
        # Ingest into vector store
        logger.info(f"Ingesting {len(documents)} documents from {file.filename}")
        ingest_document(documents)
        
        logger.info(f"Successfully processed {file.filename}")
        return UploadResponse(
            status="uploaded",
            filename=file.filename,
            chunks_ingested=len(documents)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file: {str(e)}"
        )
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                logger.debug(f"Cleaned up temp file: {temp_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {temp_path}: {e}")

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search resumes based on a query
    
    Args:
        request: SearchRequest containing query and optional top_k
        
    Returns:
        SearchResponse with answer and sources
    """
    logger.info(f"Search query received: {request.query}")
    
    # Validate query
    if not request.query or not request.query.strip():
        logger.warning("Empty query submitted")
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty. Please provide a search query."
        )
    
    if len(request.query) > 500:
        logger.warning(f"Query too long: {len(request.query)} characters")
        raise HTTPException(
            status_code=400,
            detail="Query is too long. Maximum length is 500 characters."
        )
    
    try:
        logger.info(f"Invoking RAG chain for query: {request.query}")
        response = rag_chain.invoke({"input": request.query})
        
        logger.info(f"Successfully generated response for query")
        return SearchResponse(
            answer=response,
            sources=None  # Can be extended to include source metadata
        )
        
    except Exception as e:
        logger.error(f"Search error for query '{request.query}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@app.get("/stats")
async def get_stats():
    """
    Get statistics about the document collection
    """
    try:
        from backend.database import resume_collection
        doc_count = resume_collection.count_documents({})
        
        logger.info(f"Stats requested: {doc_count} documents")
        return {
            "total_documents": doc_count,
            "status": "ready" if doc_count > 0 else "empty"
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve statistics"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error. Please try again later."}
    )