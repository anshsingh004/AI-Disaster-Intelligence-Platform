import time
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from app.core.config import settings

logger = logging.getLogger(__name__)

# Dialect-aware connection creation to support SQLite during local test pipelines
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_recycle=1800,
        pool_pre_ping=True
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    """FastAPI request-lifecycle dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def db_session():
    """Context manager for explicit transaction boundaries and clean rollback/release."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database transaction error: {str(e)}")
        raise
    finally:
        db.close()

def wait_for_db(max_retries: int = 6, retry_interval: float = 2.0) -> None:
    """Blocks execution until database connection is confirmed, retrying with backoff."""
    retries = 0
    while retries < max_retries:
        try:
            logger.info("Verifying database connection viability...")
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database connection validated successfully.")
            return
        except Exception as e:
            retries += 1
            wait_time = retry_interval * (1.5 ** (retries - 1))
            logger.warning(
                f"Database not available yet (Attempt {retries}/{max_retries}). "
                f"Retrying in {wait_time:.1f}s... Error: {str(e)}"
            )
            time.sleep(wait_time)
            
    logger.error("Database connection could not be established. Aborting startup.")
    raise RuntimeError("Database connection timed out.")
