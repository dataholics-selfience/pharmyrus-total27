"""
Celery Background Tasks for Pharmyrus
"""

import time
import logging
import traceback
from celery_app import app

logger = logging.getLogger(__name__)


@app.task(bind=True, name='pharmyrus.search')
def search_task(self, molecule: str, countries: list = None, include_wipo: bool = False):
    """
    Background task for patent search
    
    Args:
        molecule: Molecule name to search
        countries: List of country codes (default: ['BR'])
        include_wipo: Whether to include WIPO search
    
    Returns:
        Complete search results as JSON
    """
    start_time = time.time()
    
    try:
        # Update state: Starting
        self.update_state(
            state='PROGRESS',
            meta={
                'progress': 0,
                'step': 'Initializing search...',
                'elapsed': 0,
                'molecule': molecule
            }
        )
        
        logger.info(f"🚀 Starting search for: {molecule}")
        
        # Import search function (your existing code)
        from main import execute_search
        
        # Execute search with progress callback
        def progress_callback(progress: int, step: str):
            """Callback to update task progress"""
            elapsed = time.time() - start_time
            self.update_state(
                state='PROGRESS',
                meta={
                    'progress': progress,
                    'step': step,
                    'elapsed': round(elapsed, 1),
                    'molecule': molecule
                }
            )
            logger.info(f"📊 {molecule}: {progress}% - {step}")
        
        # Run the search
        result = execute_search(
            molecule=molecule,
            countries=countries or ['BR'],
            include_wipo=include_wipo,
            progress_callback=progress_callback
        )
        
        # Final update
        elapsed = time.time() - start_time
        logger.info(f"✅ Search completed for {molecule} in {elapsed:.1f}s")
        
        self.update_state(
            state='PROGRESS',
            meta={
                'progress': 100,
                'step': 'Complete!',
                'elapsed': round(elapsed, 1),
                'molecule': molecule
            }
        )
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        logger.error(f"❌ Search failed for {molecule}: {error_msg}")
        logger.error(error_trace)
        
        # Update state to FAILURE
        self.update_state(
            state='FAILURE',
            meta={
                'error': error_msg,
                'traceback': error_trace,
                'molecule': molecule,
                'elapsed': round(time.time() - start_time, 1)
            }
        )
        
        raise
