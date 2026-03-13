"""
Resume Analyzer RAG - FastAPI Server
Run with: uv run python run_server.py
"""

import uvicorn
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("="*60)
    logger.info("Resume Analyzer RAG - FastAPI Server")
    logger.info("="*60)
    logger.info("Starting server...")
    logger.info("📍 API: http://localhost:8000")
    logger.info("📚 Docs: http://localhost:8000/docs")
    logger.info("📖 ReDoc: http://localhost:8000/redoc")
    logger.info("="*60)
    
    try:
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("\n" + "="*60)
        logger.info("Server interrupted by user")
        logger.info("="*60)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
