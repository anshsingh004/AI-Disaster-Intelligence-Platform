import sys
import os

# Ensure project root is in path for ml and app package resolution
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import register_exception_handlers
from app.routers.disaster import legacy_router, v1_router
from app.routers.health import router as health_router

# Setup structured logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade APIs for disaster detection, risk assessment, and intelligence reporting",
    version="1.0.0"
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
