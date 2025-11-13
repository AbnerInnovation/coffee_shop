from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool
from typing import Generator
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

# Base class for all models
Base = declarative_base()

# Build DATABASE_URI manually to avoid property access issues
DATABASE_URI = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_SERVER}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}"

# Create database engine with connection pooling
engine = create_engine(
    DATABASE_URI,
    poolclass=QueuePool,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=settings.DB_POOL_RECYCLE,  # Recycle connections
    pool_size=settings.DB_POOL_SIZE,  # Connection pool size
    max_overflow=settings.DB_MAX_OVERFLOW,  # Max overflow connections
    pool_timeout=30,  # Timeout for getting connection from pool
    echo=settings.DB_ECHO,  # SQL logging (from config)
)


# Event listener for connection pool checkout
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Event listener when a connection is created."""
    logger.debug("Database connection established")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Event listener when a connection is checked out from the pool."""
    logger.debug("Connection checked out from pool")


# Create session factory with optimized settings
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that yields database sessions.
    
    This function:
    - Creates a new database session
    - Yields it to the caller
    - Automatically commits on success
    - Rolls back on exception
    - Always closes the session
    
    Yields:
        Session: A database session
        
    Example:
        ```python
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
        # Commit if no exception occurred
        db.commit()
    except Exception as e:
        # Rollback on any exception
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        # Always close the session
        db.close()


def get_db_context():
    """
    Context manager for database sessions.
    
    Use this for non-FastAPI code that needs a database session.
    
    Example:
        ```python
        with get_db_context() as db:
            user = db.query(User).first()
        ```
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        db.close()
