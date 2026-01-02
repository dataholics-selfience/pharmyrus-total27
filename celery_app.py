"""
Celery App Configuration for Pharmyrus
"""

import os
import logging

from celery import Celery

# Get Redis URL from Railway environment variable
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Celery app
app = Celery(
    'pharmyrus',
    broker=redis_url,
    backend=redis_url
)

# Configure
app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_send_sent_event=True,
    task_time_limit=3600,  # 60 min
    task_soft_time_limit=3300,  # 55 min
    result_expires=86400,  # 24h
    broker_connection_retry_on_startup=True,
    worker_prefetch_multiplier=1,
)

logger.info(f"🚀 Celery configured with Redis: {redis_url}")
