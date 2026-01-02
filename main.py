"""
Pharmyrus Main API - Sync & Async Endpoints
Version: v31.0.3-ASYNC
"""

import os
import logging
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from celery.result import AsyncResult

# Import your existing search modules
# NOTE: You'll need to copy your actual search code here
# For now, this is a placeholder structure

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Pharmyrus Patent Search API",
    description="Pharmaceutical Patent Intelligence System",
    version="v31.0.3-ASYNC"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SearchRequest(BaseModel):
    molecule: str
    countries: Optional[List[str]] = ["BR"]
    include_wipo: bool = False


class AsyncSearchResponse(BaseModel):
    job_id: str
    status: str
    message: str
    estimated_time: str
    endpoints: dict


class StatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    step: Optional[str] = None
    elapsed_seconds: Optional[float] = None
    message: str


# ============================================================================
# PLACEHOLDER SEARCH FUNCTION
# ============================================================================
# IMPORTANT: Replace this with your actual search code from v31.0.3

def execute_search(
    molecule: str, 
    countries: List[str], 
    include_wipo: bool = False,
    progress_callback=None
):
    """
    Main search function - REPLACE WITH YOUR ACTUAL CODE
    
    This should contain your existing search logic from v31.0.3:
    - EPO OPS search
    - Google Patents search  
    - INPI crawler
    - (Optional) WIPO search
    - Data consolidation
    
    The progress_callback allows updating task progress:
    progress_callback(50, "Searching INPI...")
    """
    import time
    
    if progress_callback:
        progress_callback(10, "Searching EPO...")
    time.sleep(2)
    
    if progress_callback:
        progress_callback(30, "Searching Google Patents...")
    time.sleep(2)
    
    if progress_callback:
        progress_callback(50, "Searching INPI...")
    time.sleep(2)
    
    if include_wipo:
        if progress_callback:
            progress_callback(60, "Searching WIPO...")
        time.sleep(5)
    
    if progress_callback:
        progress_callback(90, "Building response...")
    time.sleep(1)
    
    # PLACEHOLDER RESULT - Replace with actual search result
    result = {
        "metadata": {
            "molecule_name": molecule,
            "version": "v31.0.3-ASYNC",
            "generated_at": datetime.now().isoformat(),
            "countries": countries,
            "include_wipo": include_wipo
        },
        "patent_search": {
            "total_patents": 0,
            "note": "PLACEHOLDER - Replace execute_search() with actual code"
        }
    }
    
    return result


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Redis connection
        from celery_app import app as celery_app
        celery_app.connection().ensure_connection(max_retries=3)
        redis_status = "connected"
    except Exception as e:
        redis_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if redis_status == "connected" else "degraded",
        "version": "v31.0.3-ASYNC",
        "redis": redis_status,
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# SYNCHRONOUS ENDPOINT (Original - without WIPO)
# ============================================================================

@app.post("/search")
async def search_sync(request: SearchRequest):
    """
    Synchronous patent search (WITHOUT WIPO)
    
    Returns results immediately (5-15 minutes)
    Use for: Quick searches, testing, demos
    
    Note: Does NOT include WIPO to avoid timeout
    """
    logger.info(f"🔍 Sync search: {request.molecule}")
    
    try:
        result = execute_search(
            molecule=request.molecule,
            countries=request.countries,
            include_wipo=False  # Never include WIPO in sync
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Sync search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ASYNCHRONOUS ENDPOINTS (New - with optional WIPO)
# ============================================================================

@app.post("/search/async", response_model=AsyncSearchResponse)
async def search_async(request: SearchRequest):
    """
    Asynchronous patent search (WITH optional WIPO)
    
    Returns job_id immediately
    Use /search/status/{job_id} to track progress
    Use /search/result/{job_id} to get final result
    
    Can process searches that take 30+ minutes
    """
    from tasks import search_task
    
    logger.info(f"🚀 Async search queued: {request.molecule} (WIPO: {request.include_wipo})")
    
    # Queue the task
    task = search_task.delay(
        molecule=request.molecule,
        countries=request.countries,
        include_wipo=request.include_wipo
    )
    
    estimated_time = "30-60 minutes" if request.include_wipo else "5-15 minutes"
    
    return AsyncSearchResponse(
        job_id=task.id,
        status="queued",
        message=f"Search started for {request.molecule}. Use status endpoint to track progress.",
        estimated_time=estimated_time,
        endpoints={
            "status": f"/search/status/{task.id}",
            "result": f"/search/result/{task.id}",
            "cancel": f"/search/cancel/{task.id}"
        }
    )


@app.get("/search/status/{job_id}", response_model=StatusResponse)
async def get_search_status(job_id: str):
    """
    Get status and progress of an async search
    
    Frontend should poll this endpoint every 5-10 seconds
    """
    task = AsyncResult(job_id)
    
    if task is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Queued
    if task.state == 'PENDING':
        return StatusResponse(
            job_id=job_id,
            status="queued",
            progress=0,
            message="Job is queued, waiting to start..."
        )
    
    # Running with progress
    elif task.state == 'PROGRESS':
        info = task.info or {}
        return StatusResponse(
            job_id=job_id,
            status="running",
            progress=info.get('progress', 0),
            step=info.get('step', 'Processing...'),
            elapsed_seconds=info.get('elapsed', 0),
            message=f"Currently: {info.get('step', 'Processing...')}"
        )
    
    # Complete
    elif task.state == 'SUCCESS':
        return StatusResponse(
            job_id=job_id,
            status="complete",
            progress=100,
            message="Search completed successfully! Use /search/result to get data."
        )
    
    # Failed
    elif task.state == 'FAILURE':
        error_info = task.info or {}
        return StatusResponse(
            job_id=job_id,
            status="failed",
            progress=0,
            message=f"Search failed: {error_info.get('error', 'Unknown error')}"
        )
    
    # Other states
    else:
        return StatusResponse(
            job_id=job_id,
            status=task.state.lower(),
            progress=0,
            message=f"Job state: {task.state}"
        )


@app.get("/search/result/{job_id}")
async def get_search_result(job_id: str):
    """
    Get complete search results
    
    Only works when status is 'complete'
    Results are stored for 24 hours
    """
    task = AsyncResult(job_id)
    
    if task.state != 'SUCCESS':
        raise HTTPException(
            status_code=400,
            detail=f"Result not ready. Current status: {task.state}. Use /search/status/{job_id}"
        )
    
    return task.result


@app.delete("/search/cancel/{job_id}")
async def cancel_search(job_id: str):
    """
    Cancel a running search
    
    Note: May not stop immediately if deep in processing
    """
    task = AsyncResult(job_id)
    
    if task.state in ['PENDING', 'PROGRESS']:
        task.revoke(terminate=True)
        logger.info(f"🛑 Job cancelled: {job_id}")
        return {
            "job_id": job_id,
            "status": "cancelled",
            "message": "Job cancelled successfully"
        }
    else:
        return {
            "job_id": job_id,
            "status": task.state.lower(),
            "message": f"Cannot cancel job in state: {task.state}"
        }


# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    logger.info("=" * 60)
    logger.info("🚀 Pharmyrus API v31.0.3-ASYNC Starting...")
    logger.info("=" * 60)
    
    # Test Redis connection
    try:
        from celery_app import app as celery_app
        celery_app.connection().ensure_connection(max_retries=3)
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        logger.warning("⚠️  Async features will not work!")
    
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown tasks"""
    logger.info("👋 Pharmyrus API shutting down...")


# ============================================================================
# RUN (for local development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
