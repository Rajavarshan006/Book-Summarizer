"""
API Service for Text Summarization
This module provides REST API endpoints for text chunk summarization
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import logging
from datetime import datetime

# Import performance logger
from utils.performance_logger import get_performance_logger

# Import local modules
from backend.pipeline import PreprocessingPipeline
from models.t5_summarizer import summarize_text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Text Summarization API",
    description="API for generating summaries from preprocessed text chunks",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

class TextChunk(BaseModel):
    """Model for a single text chunk"""
    text: str
    chunk_id: Optional[str] = None
    metadata: Optional[dict] = None

class SummarizationRequest(BaseModel):
    """Request model for summarization API"""
    chunks: List[TextChunk]
    max_length: Optional[int] = 150
    min_length: Optional[int] = 40
    model_params: Optional[dict] = None

class SummarizationResponse(BaseModel):
    """Response model for summarization API"""
    success: bool
    summaries: List[str]
    chunk_summaries: List[dict]
    processing_time: float
    timestamp: str
    error: Optional[str] = None

@app.post("/summarize", response_model=SummarizationResponse)
async def summarize_chunks(request: SummarizationRequest):
    """
    API endpoint that accepts preprocessed text chunks and returns generated summaries

    Args:
        request: SummarizationRequest containing text chunks and parameters

    Returns:
        SummarizationResponse with generated summaries and metadata
    """
    start_time = datetime.now()
    performance_logger = get_performance_logger()

    # Log API request with performance tracking
    performance_logger.logger.info(f"Received summarization request with {len(request.chunks)} chunks")
    api_start_time = performance_logger.start_timer()

    try:
        # Validate input
        if not request.chunks:
            raise HTTPException(status_code=400, detail="No text chunks provided")

        summaries = []
        chunk_summaries = []
        success_count = 0
        error_count = 0

        # Process each chunk
        for i, chunk in enumerate(request.chunks):
            try:
                chunk_start = datetime.now()

                # Generate summary for this chunk
                summary = summarize_text(
                    chunk.text,
                    max_length=request.max_length,
                    min_length=request.min_length
                )

                chunk_end = datetime.now()
                chunk_processing_time = (chunk_end - chunk_start).total_seconds()

                # Store chunk metadata
                chunk_summary = {
                    "chunk_id": chunk.chunk_id or f"chunk_{i+1}",
                    "summary": summary,
                    "processing_time": round(chunk_processing_time, 4),
                    "character_count": len(chunk.text),
                    "word_count": len(chunk.text.split()),
                    "metadata": chunk.metadata or {}
                }

                summaries.append(summary)
                chunk_summaries.append(chunk_summary)
                success_count += 1

                logger.info(f"Processed chunk {i+1}/{len(request.chunks)} - {len(summary)} chars")

            except Exception as e:
                logger.error(f"Error processing chunk {i+1}: {str(e)}")
                chunk_summaries.append({
                    "chunk_id": chunk.chunk_id or f"chunk_{i+1}",
                    "error": str(e),
                    "processing_time": 0.0
                })
                summaries.append(None)  # Add placeholder to maintain list alignment
                error_count += 1
                continue

        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        # Log total processing performance
        performance_logger.log_total_processing(
            total_time=processing_time,
            chunk_count=len(request.chunks),
            success_count=success_count,
            error_count=error_count
        )

        response = SummarizationResponse(
            success=len(summaries) > 0,
            summaries=summaries,
            chunk_summaries=chunk_summaries,
            processing_time=round(processing_time, 4),
            timestamp=datetime.now().isoformat(),
            error=None if len(summaries) > 0 else "All chunks failed to process"
        )

        logger.info(f"Successfully processed {len(request.chunks)} chunks in {processing_time:.2f} seconds")
        return response

    except Exception as e:
        logger.error(f"Summarization failed: {str(e)}")
        performance_logger.log_error(
            error_type="API_ERROR",
            error_message=str(e),
            context={"endpoint": "/summarize", "chunk_count": len(request.chunks)}
        )
        raise HTTPException(
            status_code=500,
            detail=f"Summarization failed: {str(e)}"
        )

@app.post("/summarize-preprocessed", response_model=SummarizationResponse)
async def summarize_preprocessed_text(request: SummarizationRequest):
    """
    Alternative endpoint that accepts preprocessed text chunks
    This endpoint assumes the text has already been cleaned and chunked

    Args:
        request: SummarizationRequest containing preprocessed text chunks

    Returns:
        SummarizationResponse with generated summaries
    """
    return await summarize_chunks(request)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Text Summarization API"
    }

if __name__ == "__main__":
    logger.info("Starting Text Summarization API server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )
