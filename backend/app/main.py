import sys
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is in path for ml and app package resolution
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import register_exception_handlers
from app.routers.disaster import legacy_router, v1_router
from app.routers.health import router as health_router
from app.db import wait_for_db
from app.db_seeder import seed_database
from alembic.config import Config
from alembic import command

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the startup and shutdown lifecycle tasks of the FastAPI application."""
    # 1. Blocks until PostgreSQL is ready to receive requests
    wait_for_db()
    
    # 2. Applies migrations automatically to initialize database
    logger.info("Executing automatic schema migration upgrades...")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    logger.info("Automatic database migrations completed.")
        
    # 3. Seeds database with operational alerts and report templates
    try:
        seed_database()
    except Exception as e:
        logger.error(f"Automatic database seeding failed: {str(e)}")

    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade APIs for disaster detection, risk assessment, and intelligence reporting",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handlers
register_exception_handlers(app)

# Register Routers
app.include_router(health_router)
app.include_router(legacy_router)
app.include_router(v1_router)
