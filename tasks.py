"""
Celery Background Tasks for Pharmyrus
Wraps the existing search logic with progress tracking
"""

import time
import logging
import traceback
from celery_app import app

logger = logging.getLogger(__name__)


@app.task(bind=True, name='pharmyrus.search')
def search_task(self, nome_molecula: str, nome_comercial: str = None, paises_alvo: list = None, include_wipo: bool = False):
    """
    Background task for patent search
    
    Args:
        nome_molecula: Molecule name
        nome_comercial: Commercial/brand name (optional)
        paises_alvo: List of target countries (default: ['BR'])
        include_wipo: Whether to include WIPO search (Future)
    
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
                'molecule': nome_molecula
            }
        )
        
        logger.info(f"🚀 Starting async search for: {nome_molecula}")
        
        # Import search function from main (existing working code)
        from main import execute_search_sync
        
        # Create progress callback
        def progress_callback(progress: int, step: str):
            """Callback to update task progress"""
            elapsed = time.time() - start_time
            self.update_state(
                state='PROGRESS',
                meta={
                    'progress': progress,
                    'step': step,
                    'elapsed': round(elapsed, 1),
                    'molecule': nome_molecula
                }
            )
            logger.info(f"📊 {nome_molecula}: {progress}% - {step}")
        
        # Run the search (wraps existing async function)
        import asyncio
        result = asyncio.run(
            execute_search_sync(
                nome_molecula=nome_molecula,
                nome_comercial=nome_comercial,
                paises_alvo=paises_alvo or ['BR'],
                include_wipo=include_wipo,
                progress_callback=progress_callback
            )
        )
        
        # Final update
        elapsed = time.time() - start_time
        logger.info(f"✅ Search completed for {nome_molecula} in {elapsed:.1f}s")
        
        self.update_state(
            state='PROGRESS',
            meta={
                'progress': 100,
                'step': 'Complete!',
                'elapsed': round(elapsed, 1),
                'molecule': nome_molecula
            }
        )
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        logger.error(f"❌ Search failed for {nome_molecula}: {error_msg}")
        logger.error(error_trace)
        
        # Update state to FAILURE
        self.update_state(
            state='FAILURE',
            meta={
                'error': error_msg,
                'traceback': error_trace,
                'molecule': nome_molecula,
                'elapsed': round(time.time() - start_time, 1)
            }
        )
        
        raise
