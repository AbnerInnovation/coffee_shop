"""
Application lifespan management.

Handles startup and shutdown events, including background tasks.
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from ..db.base import get_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Handles background tasks like flushing special note statistics.
    
    Args:
        app_instance: FastAPI application instance
    """
    # Startup
    logger.info("Starting background tasks...")
    
    # Create background task for flushing special note stats
    task = asyncio.create_task(_flush_special_notes_task())
    
    yield
    
    # Shutdown
    logger.info("Shutting down background tasks...")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


async def _flush_special_notes_task():
    """
    Background task that flushes special note statistics every 5 minutes.
    """
    from ..services.special_notes import SpecialNotesService
    
    while True:
        try:
            await asyncio.sleep(300)  # 5 minutes
            
            # Get a database session
            db = next(get_db())
            try:
                updated_count = SpecialNotesService.flush_updates(db)
                if updated_count > 0:
                    logger.info(f"Flushed {updated_count} special note updates to database")
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in special notes flush task: {str(e)}", exc_info=True)
