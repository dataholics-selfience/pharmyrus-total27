"""
Celery App Configuration for Pharmyrus
"""

import os
import logging

from celery import Celery

# Get Redis URL from environment
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery app
app = Celery(
    'pharmyrus',
    broker=redis_url,
    backend=redis_url
)

# Configure Celery
app.conf.update(
    # Serialization
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    
    # Timezone
    timezone='UTC',
    enable_utc=True,
    
    # Task tracking
    task_track_started=True,
    task_send_sent_event=True,
    
    # Timeouts (1 hour for WIPO)
    task_time_limit=3600,  # 60 minutes hard limit
    task_soft_time_limit=3300,  # 55 minutes soft limit
    
    # Result expiration
    result_expires=86400,  # 24 hours
    
    # Connection retry
    broker_connection_retry_on_startup=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"🚀 Celery configured with Redis: {redis_url}")
