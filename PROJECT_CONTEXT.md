# PROJECT_CONTEXT.md: Terra-Aura Engineering Specification

This document serves as the permanent engineering specification for the Terra-Aura platform. It outlines the architectural blueprints, technical standards, deployment topologies, and roadmap configurations.

---

## 1. Project Vision
Terra-Aura is a production-grade AI Disaster Intelligence Platform. It correlates meteorological signals, social indicators, and spatial sensor feeds in near real-time to compute predictive threat indicators.

Unlike simple CRUD platforms, Terra-Aura operates as an active threat engine:
- **Spatial Processing:** Correlates incidents geographically using spatial dimensions.
- **Predictive Ingest:** Evaluates risk categorization and threat propagation probabilities immediately upon sensor ingestion.
- **Auditable Operations:** Logs operator acknowledgments and system settings for emergency audit trails.

Target users include EOC operators, climate analysts, and field teams. The codebase serves as a showcase portfolio demonstrating robust software engineering, modular monolith patterns, and modern DevOps configurations.

---

## 2. Current Architecture
The platform is structured as a **Modular Monolith** containing isolated domains for web APIs, machine learning pipelines, and relational storage.

```mermaid
graph TD
    User[EOC Operators] -->|Web Browser| Frontend[React Single Page App]
    Frontend -->|REST APIs| Backend[FastAPI Application Server]
    Backend -->|SQLAlchemy + QueuePool| DB[(PostgreSQL Database)]
    Backend -->|Local Function Calls| ML[Inference Proxy ml/inference]
```

- **Frontend Client:** React SPA communicating with backend services via REST.
- **FastAPI Application Server:** Exposes routing controllers. Contains versioned APIs (`/api/v1/...`) and root-level legacy handlers.
- **Inference Layer:** Computationally isolated rules proxy executing deterministic threat algorithms.
- **Database Layer:** Structured Postgres storing historical events. Managed by Alembic.

---

## 3. Technology Stack

### Frontend
- **Framework:** React 19.x (Single Page App)
- **Maps:** Leaflet 1.9.x / React-Leaflet 5.x
- **HTTP Client:** Axios 1.13.x
- **Styling:** Vanilla CSS (curated high-contrast color variables)

### Backend
- **Framework:** FastAPI 0.124.x
- **Web Server:** Uvicorn 0.38.x
- **ORM:** SQLAlchemy 2.0.x (Synchronous configuration)
- **Validation:** Pydantic 2.12.x / Pydantic-Settings 2.14.x

### Database & Migrations
- **Engine:** PostgreSQL 15-alpine
- **Adapter:** psycopg2-binary 2.9.x
- **Migrations:** Alembic 1.18.x

### AI & Inference
- **Inference Engine:** Rules proxy (`ml/inference/predict.py`)
- **Libraries:** NumPy, Pandas, Scikit-learn, PyTorch, OpenCV-python (declared in requirements)

### DevOps & Tooling
- **Orchestration:** Docker / Docker Compose
- **Quality Assurance:** Pre-commit hooks (Black, Ruff, ESLint, Prettier)
- **Version Control:** Git

---

## 4. Folder Structure
The repository is organized cleanly by domain boundaries:

```txt
/
├── .github/workflows/      # Future CI/CD configurations
├── .gitignore              # Root Git exclusion specifications
├── .pre-commit-config.yaml # Pre-commit hook definitions
├── docker-compose.yml      # Service orchestration manifest
├── docs/                   # Engineering design documents
├── ml/                     # ML code, sample data, and inference logic
│   ├── inference/
│   │   └── predict.py      # ML Rules proxy
│   └── Requirements.txt    # ML dependencies
├── backend/
│   ├── alembic/            # Database migration history
│   ├── alembic.ini         # Alembic configuration metadata
│   ├── Dockerfile          # Multi-stage Python build script
│   ├── requirements.txt    # API dependency definitions
│   ├── .env.example        # Environment settings template
│   ├── .env                # Local secrets configuration
│   └── app/
│       ├── main.py         # FastAPI bootloader and app assembly
│       ├── db.py           # Engine & connection pool configuration
│       ├── core/           # Core cross-cutting modules
│       │   ├── config.py   # Settings validation
│       │   ├── logging.py  # Structured logger configurations
│       │   ├── response.py # JSON response envelopes
│       │   └── exceptions.py # Global handlers
│       ├── models/         # SQLAlchemy models
│       ├── schemas/        # Validation schemas
│       ├── services/       # Core business logic handlers
│       └── routers/        # FastAPI endpoint controllers
└── frontend/
    ├── Dockerfile          # Nginx-based React production build
    ├── package.json        # Node modules and scripts
    └── src/                # React client sources
```

---

## 5. Database Design

### disasters Table Schema
Stores assessed threat incidents:
- `id` (Integer, Primary Key)
- `disaster_type` (String, Indexed)
- `severity_score` (Float)
- `risk_level` (String, Indexed)
- `population_at_risk` (Integer)
- `confidence` (Float)
- `latitude` (Float)
- `longitude` (Float)
- `created_at` (DateTime, Indexed)

### Migration Management
Managed via Alembic scripts inside `backend/alembic/`. Autogenerate configurations track changes directly from the declarative `Base` meta classes. Running `alembic upgrade head` applies pending changes transactionally.

### Connection Pooling
Synchronous connection pooling is handled by `QueuePool` on `create_engine`:
- `pool_size=10`
- `max_overflow=20`
- `pool_recycle=1800`
- `pool_pre_ping=True`

---

## 6. API Design Principles

### Path Versioning
New endpoints are mounted under the `/api/v1` namespace. Legacy routes are maintained at the root for backward compatibility.

### Standard Response Envelope
All versioned endpoint payloads conform to this envelope structure:
```json
{
  "success": true,
  "data": {},
  "error": null,
  "timestamp": "2026-07-05T06:07:20Z"
}
```

### Global Error Handling
Global handlers catch `HTTPException`, validation errors (`RequestValidationError`), and system failures, formatting them into the response envelope with clean message logs.

---

## 7. AI Pipeline
- **Current Setup:** Ingest coordinates and signals; compute classifications and scores via deterministic logic in [predict.py](file:///x:/college/Projects/AI-Disaster-Intelligence-Platform/ml/inference/predict.py).
- **Abstractions:** Services interact with models using an abstract class framework. This allows swapping the local rules proxy for real model weights (ONNX/PyTorch runtimes) with zero modifications to routers.

---

## 8. Authentication Strategy
- *Pending Implementation*
- **Planned Target:** Enforce token authentication checks on `/api/v1` routers using Supabase Auth JWT validation. The API server will parse and verify JWT signatures without local password storage.

---

## 9. Background Processing
- *Pending Implementation*
- **Planned Target:** Offload weather polling and RAG compilation to Celery workers backed by a Redis message broker.

---

## 10. RAG Pipeline
- *Pending Implementation*
- **Planned Target:** Process historical disaster alerts and operational logs, index them in ChromaDB as vector embeddings, and retrieve relevant logs for Gemini LLM context to compile situation reports.

---

## 11. Infrastructure
Services run in isolated Docker containers linked via docker-compose networking:
- **disaster_db:** Postgres 15 database instance using volume mounting for persistence.
- **disaster_backend:** FastAPI application server running Uvicorn.
- **disaster_frontend:** React SPA served via Nginx.

---

## 12. Deployment Strategy
- **Local Dev:** Launched via `docker-compose up --build` or manual python execution.
- **Production Target:** Backend deployed on Render, frontend hosted on Vercel, and database hosted on Supabase Postgres.

---

## 13. Environment Variables
Defined in `.env` and settings configurations:
- `ENV` (e.g. `development`, `production`)
- `LOG_LEVEL` (e.g. `INFO`, `WARNING`)
- `DATABASE_URL` (SQLAlchemy postgresql connection string)

---

## 14. Coding Standards
- **Python:** PEP 8 styling. Formatted via Black and linted via Ruff.
- **JavaScript:** ESLint lint rules and Prettier formatting.
- **Commits:** Conventional Commits: `type(scope): message`.

---

## 15. Current Limitations
- AI module is limited to a deterministic rules engine proxy.
- Frontend dashboard metrics represent static local arrays, not linked to APIs.
- Authentication validation and background task queuing are pending setup.

---

## 16. Future Roadmap
- **Phase 1:** Core Production Infrastructure Upgrade (Completed).
- **Phase 2:** API integration with frontend templates and real-time weather polling.
- **Phase 3:** RAG compilation framework (ChromaDB + Gemini).
- **Phase 4:** Model serving pipeline (ONNX Runtime).

---

## 17. Decisions Made
- **Sync DB Executions:** Used synchronous SQLAlchemy with `QueuePool` connection pooling rather than `AsyncSession` to maintain architectural simplicity.
- **Multi-stage Containers:** Used multi-stage Docker builds to keep production image footprints under 150MB.
- **Legacy Compatibility:** Staged both enveloped `/api/v1` routes and raw legacy endpoints to prevent breaking changes.

---

## 18. Breaking Changes
- No breaking changes were introduced during Phase 1. Legacy endpoints remain operational.

---

## 19. Pending Work
- Refactor the React pages to fetch and send data using the new versioned backend API endpoints.
- Configure token checks in routing dependencies.

---

## 20. Production Readiness Checklist
- [x] Environment variables validated (Pydantic-Settings).
- [x] Production connection pooling enabled (QueuePool).
- [x] Versioned migrations configured (Alembic).
- [x] Standard API envelopes and global error handlers active.
- [x] Multi-container orchestration defined (Docker Compose).
- [ ] Authentication check middleware enabled.
- [ ] Real ML model weights serving active.
- [ ] Telemetry logging and daily backup schemes configured.
