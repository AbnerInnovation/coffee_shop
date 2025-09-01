import logging
from sqlalchemy import text
from .base import engine, Base
from ..models import *  # Import all models to register them with SQLAlchemy

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    """
    Initialize the database by creating all tables.
    """
    logger.info("Creating database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            
        logger.info(f"Successfully created {len(tables)} tables: {', '.join(tables)}")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def drop_db() -> None:
    """
    Drop all database tables (use with caution in production).
    """
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("All database tables dropped.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        drop_db()
    
    init_db()
