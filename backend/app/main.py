import sys
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is in path for ml and app package resolution
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import register_exception_handlers
from app.routers.disaster import legacy_router, v1_router
from app.routers.auth import router as auth_router
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
    wait_for_db()
    
    try:
        logger.info("Executing automatic schema migration upgrades...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Automatic database migrations completed.")
    except Exception as e:
        logger.error(f"Automatic database migration failed: {str(e)}")
        raise
        
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
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inject HTTP Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Exclude CSP on Swagger/Redoc routes to prevent breaking stylesheet CDNs
    path = request.url.path
    if not any(path.startswith(p) for p in ["/docs", "/redoc", "/openapi.json"]):
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
    return response

# Register Exception Handlers
register_exception_handlers(app)

# Register Routers
app.include_router(health_router)
app.include_router(legacy_router)
app.include_router(v1_router)
app.include_router(auth_router)
