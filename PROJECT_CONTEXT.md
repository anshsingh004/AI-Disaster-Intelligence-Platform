# Project Vision

## Purpose
Terra-Aura is a production-grade AI Disaster Intelligence Platform designed to ingest, process, predict, and visualize environmental hazards and disaster risks in near real-time. The platform correlates multi-source signals (meteorological data, social indicators, satellite sensor data) to deliver high-confidence predictive threat intelligence. The primary goal is to demonstrate a production-ready application of Full Stack, AI, Backend, Cloud, and DevOps engineering principles.

## Target Users
- **Emergency Operations Center (EOC) Operators:** Personnel coordinating tactical responses who require a unified, low-latency spatial and incident map dashboard.
- **Geospatial & Climate Analysts:** Domain specialists who analyze predictive severity models and export historical risk logs for reporting.
- **First Responders & Field Teams:** Tactical units relying on broadcast alerts, incident feeds, and RAG-generated situation reports.

## Engineering Goals
- Establish an enterprise-ready modular monolith architecture with clean separations of concern.
- Achieve sub-second response times on spatial and predictive queries.
- Build a resilient, self-healing system with comprehensive health diagnostics.
- Ensure the codebase serves as an elite portfolio project demonstrating deep technical competence to top-tier engineering organizations.

## CRUD vs. Disaster Intelligence Differentiators
Unlike conventional CRUD applications that merely persist and retrieve user records, Terra-Aura operates as a data engine:
- **Spatial Processing:** Standard database rows are augmented with geospatial coordinates, demanding geometric calculations and spatial indexing.
- **Predictive ML Pipelines:** API endpoints run real-time, deterministic or machine-learning-based inference steps upon ingest rather than simple transactional inserts.
- **Multi-Source Synthesis:** Features correlate external sensor feeds (weather conditions, social sentiment scores) to dynamically calculate risk level escalations.
- **Observability and Status Verification:** The system exposes deep infrastructure health, model version tracking, and user audit logs.

---

# Product Goals

The platform delivers the following major product capabilities:

- **Disaster Monitoring:** Real-time visual tracking of active environmental threats across geographic sectors.
- **AI Analysis:** Automated estimation of disaster type, risk categorization, severity score, and population impact using current signal values.
- **Geospatial Intelligence:** Interactive map overlays containing spatial markers, risk-level color codes, and location tracking.
- **RAG-powered Situation Reports:** Automated generation of contextual operational reports combining historical database records and external documentation.
- **Resource Management:** Tactical response tracking, equipment allocation log states, and user profile role assignments.
- **Incident Tracking:** Step-by-step lifecycles of active incidents from detection, to acknowledgment, to final resolution.
- **Analytics Dashboard:** Unified dashboard presenting average confidence metrics, historical trends, sector risk distributions, and data exporting utilities.

---

# Engineering Principles

- **Modular Monolith:** Organize the application by discrete domain boundaries (ML, API Routers, Database, Services) within a single deployable artifact to reduce operational and network complexity while enabling an easy future split into microservices if needed.
- **Production First:** Write all code, environment variables, configuration schemas, and error boundaries with the assumption that the system will run on public production nodes. Do not rely on "localhost" shortcuts.
- **Backward Compatibility:** Maintain API schema stability and database schema migrations across updates to prevent breaking live frontend components.
- **Security First:** Enforce authentication checkpoints, strict input validation ranges, least-privilege database roles, and standard CORS policies.
- **Clean Architecture:** Keep business rules and domain logic decoupled from framework-specific dependencies (such as FastAPI internals or SQLAlchemy ORM structures).
- **SOLID & DRY:** Apply standard object-oriented design and modular reuse. Prevent duplicate models, schemas, and utilities across domain layers.
- **Simplicity over Complexity:** Reject premature microservice separation, message brokers, and complex caching strategies until raw throughput demands them.
- **Feature Completeness over Tech Hype:** Deliver solid, fully realized endpoints, tests, and documentation rather than integration of unproven beta frameworks.
- **Enterprise Standards:** Ensure descriptive variable naming, comprehensive typing, rigorous error handling blocks, and detailed docstrings across all modules.

---

# Current Technology Stack

## Frontend
- **Framework:** React 19.x (Standard Single Page App structure)
- **Geospatial Rendering:** Leaflet 1.9.x / React-Leaflet 5.x
- **HTTP Client:** Axios 1.13.x
- **Styling:** Vanilla CSS (curated high-end color systems and layouts)

## Backend
- **Framework:** FastAPI 0.124.x
- **Server:** Uvicorn 0.38.x
- **ORM:** SQLAlchemy (Synchronous) + QueuePool for production-grade connection pooling
- **Validation:** Pydantic 2.12.x

## Database
- **Primary Engine:** PostgreSQL
- **Database Adapter:** psycopg2-binary 2.9.x

## AI
- **Inference Proxy:** Pure Python-based rules engine (`ml/inference/predict.py`)
- **Core ML Dependencies (in requirements):** NumPy, Pandas, Scikit-learn, PyTorch, OpenCV-python

## GIS
- **Spatial Extensions:** GeoAlchemy2 0.18.x (configured for PostgreSQL GIS integrations)
- **Map Visuals:** React-Leaflet/Leaflet

## Authentication
- *None currently implemented* (Auth structures are stubbed in frontend UI mockups)

## Deployment
- *None currently implemented* (Development environment restricted to local localhost configurations)

## Infrastructure
- **Development Database:** Local PostgreSQL server instance

## Developer Tools
- **Version Control:** Git
- **Interactive Documentation:** Swagger UI (FastAPI `/docs` endpoint)

---

# Planned Technology Roadmap

- **Alembic:** Declarative database schema migrations.
- **Docker Compose:** Multi-container orchestration (FastAPI, PostgreSQL, Redis, Celery).
- **Redis:** Latency reduction via database caching and API rate-limiting middleware.
- **Celery:** Asynchronous task queueing for weather signal polls and heavy ML runs.
- **GitHub Actions:** Automated CI/CD pipeline (lint checks, pytest suites, build packaging).
- **Prometheus & Grafana:** Instrumentation for CPU, RAM, database connection pools, and endpoint latency metrics.
- **ONNX Runtime:** ONNX Runtime with a Model Serving Abstraction Layer, keeping the architecture compatible with future Ray Serve integration.
- **Incremental RAG:** Vector database syncing pipeline and semantic document searches.
- **Background Workers:** Worker processes handling report compilations and audit log archiving.
- **Rate Limiting:** IP-based requests-per-minute constraints on endpoints.
- **Caching:** Temporary storage of weather data queries.
- **Health Checks:** Comprehensive `/health` diagnostic endpoints testing database, network, and disk performance.
- **Production Logging:** Structured JSON logging for downstream log aggregation tools.

---

# Architecture Decisions

- **Modular Monolith over Microservices:** Reduces debugging overhead, minimizes network calls, and speeds up feature velocity during early phases. Boundaries are strictly drawn using directory structures to allow future extraction.
- **Docker-First Development:** Ensures development environments exactly match staging/production configurations, preventing "works on my machine" issues.
- **PostgreSQL with Synchronous SQLAlchemy:** Utilizes PostgreSQL as primary database with SQLAlchemy (Synchronous) + QueuePool for production-grade connection pooling instead of asynchronous database drivers to ensure simplicity and stable transaction handling under high traffic.
- **ChromaDB for Vector Storage:** Selected as an embedded vector database for RAG pipeline embeddings, minimizing infrastructure complexity.
- **FastAPI for Backend APIs:** Offers native async event handling, high throughput, autogenerated OpenAPI schemas, and Pydantic data serialization.
- **ONNX Runtime with Model Serving Abstraction:** Uses ONNX Runtime with a Model Serving Abstraction Layer, keeping the architecture compatible with future Ray Serve integration.
- **React for Frontend:** Structured as a component-driven React dashboard to keep client-side spatial updates and UI states highly responsive.
- **AI Modules Separated from API Layer:** Machine Learning execution modules exist inside a separate root directory (`ml/`), isolating compute-heavy packages from web API runtimes.
- **Environment Variable Configuration:** Standard 12-factor configuration using `.env` files and Pydantic settings base to prevent hardcoding of credentials.
- **REST APIs Only:** Simple RESTful interfaces utilizing standardized JSON schemas ensure predictability and robust client compatibility.
- **Free/Open-Source Infrastructure:** Ensure the stack fits within free tiers of platforms like Render, Vercel, and Supabase to maintain a zero-cost portfolio profile.

---

# Database Principles

- **Normalization:** Enforce Third Normal Form (3NF) across core business models (Disasters, Alerts, Reports) to eliminate redundancy and maintain database consistency.
- **Migrations:** All database modifications must be managed via Alembic scripts. Manual modification of tables in production is strictly forbidden.
- **Indexes:** Standard B-tree indexes are implemented on query targets (`created_at`, `risk_level`, `disaster_type`). Spatial columns will leverage GiST indexing to optimize geo-queries.
- **Referential Integrity:** Enforce foreign key constraints with strict cascade delete policies. Maintain data consistency through constraint checks (e.g., coordinate boundaries check).
- **Future Scalability:** Design schemas to support horizontal partitioning by timestamp or sector ID if read-write traffic spikes.

---

# API Design Principles

- **Consistent Response Structure:** All responses conform to standard JSON patterns. Successful endpoints return resources directly or wrapped in standard paginated envelopes:
  ```json
  {
    "items": [...],
    "page": 1,
    "page_size": 10,
    "total": 100
  }
  ```
- **Error Handling:** Standard HTTP status codes are utilized (e.g., 400, 401, 403, 404, 422, 500). Custom exceptions map directly to structured JSON error objects containing specific error codes and messages.
- **Versioning Strategy:** APIs are prefixed with version markers in the URL path: `/api/v1/...`. Changes to schemas require a major version bump if backward compatibility is broken.
- **Validation:** Pydantic handles automatic coercion, bounds checking, and strict type verification at the ingress layer. Invalid payloads are immediately rejected with a `422 Unprocessable Entity` status.
- **Authentication:** Bearer token authorization checks are enforced on protected routes.
- **REST Conventions:** Use clear resource naming (nouns), appropriate verbs (`GET`, `POST`, `PATCH`, `DELETE`), and query parameters for filtering/pagination.

---

# AI System Design

- **Satellite Classification:** *Future Architectural Blueprint* – Ingestion pipeline for imagery files, utilizing deep learning models to output binary classifications of burn scars, flood basins, or structural collapses.
- **Weather Risk Prediction:** Environmental risk evaluation leveraging meteorology parameters. Runs mathematical baseline rules and maps values directly to localized hazard categories.
- **Tweet Analysis:** Natural Language Processing (NLP) module parsing feeds to extract locations, disaster classifications, and damage descriptions.
- **Retrieval-Augmented Generation (RAG):** Document chunking, vector embedding, and similarity search pipelines to generate comprehensive emergency situation reports.
- **ONNX Support:** Future integration to execute models compiled to ONNX format, decoupling the inference runtime from heavy PyTorch or TensorFlow runtimes.
- **Model Serving Abstraction:** API layer connects to model inferences using an abstract interface class, allowing swapping of internal model engines (rules proxy, local ONNX, cloud API) with zero modifications to routers.
- **Prompt Management:** Version-controlled template files mapping structured inputs to prompt strings for natural language generation.

---

# Security Principles

- **Authentication Philosophy:** Delegate identity management to external auth providers (Supabase Auth) to avoid storing salted/hashed user passwords locally.
- **JWT (JSON Web Tokens):** Use verified, cryptographically signed JWTs passed in headers.
- **Role-Based Access Control (RBAC):** Enforce path or service-level access checks matching user profile clearance fields (`ClearanceLevel`, `Role`).
- **Environment Variables:** All application secrets, database keys, and configuration overrides must be injected via runtime environment variables.
- **Secrets Management:** Secrets are stored securely in target hosting platforms, never checked into version control.
- **Input Validation:** Enforce strict size limitations on file uploads, sanitization on query strings, and value range constraints on environmental input parameters.
- **Audit Logging:** Systematically track write actions, login failures, profile updates, and administrative overrides in a dedicated `audit_logs` table.
- **Rate Limiting:** Throttle requests on high-impact routes (such as authentication or inference submissions) to protect backend availability.
- **Future Security Improvements:** Multi-factor authentication (MFA) enforcement and restricted IP address range checks for EOC administrator routes.

---

# Infrastructure Strategy

- **Deployment Philosophy:** Automate the build, verification, and hosting pipeline to ensure rapid, repeatable deployments.
- **Docker Integration:** Construct multi-stage Dockerfiles separating build steps from runtime execution configurations.
- **Docker Compose:** Mirror production setup in local development environments.
- **Production Hosting:** 
  - Backend API: Hosted on cloud platform services (e.g., Render, Supabase).
  - Frontend App: Served from global CDN platforms (e.g., Vercel).
  - Database: Relational cloud Postgres (e.g., Supabase PostgreSQL).
- **CI/CD Pipeline:** Deploy automatically from target git branch (e.g., `main`, `release`) following passing status checks.
- **Telemetry & Monitoring:** Implement system health metrics dashboards, capturing response latency percentiles and system resource bottlenecks.
- **Logging:** Output stdout logs in a flat, readable schema or structured JSON logs for log ingestion utilities.
- **Health Endpoints:** Expose dynamic endpoints `/health` and `/system/status` checking database status, memory utilization, and external API states.
- **Backups:** Enforce database snapshot intervals, maintaining transaction log records.
- **Disaster Recovery:** Formulate failover configuration guidelines to restore operational states within defined target time goals.

---

# Coding Standards

- **Naming Conventions:**
  - Python (Backend/ML): `snake_case` for variables, functions, and file names; `PascalCase` for classes; `UPPER_CASE` for constants.
  - JavaScript (Frontend): `camelCase` for variables and functions; `PascalCase` for components and classes.
- **Folder Structure:**
  ```txt
  /
  ├── ml/             # ML pipelines, datasets, and inference modules
  ├── backend/        # FastAPI application, database schemas, and service logic
  ├── frontend/       # React client code, layouts, styling, and maps
  └── docs/           # Architecture diagrams, API specs, and plan details
  ```
- **Comments and Documentation:** Code must be self-documenting. Use clear variables rather than excessive comments. Document complex helper algorithms, and write PEP-257 compliant docstrings on all backend modules, classes, and public functions.
- **Error Handling:** Avoid broad exception traps. Catch specific exceptions (e.g., `SQLAlchemyError`, `KeyError`) and raise corresponding client-safe HTTP exceptions with clean descriptive context.
- **Code Formatting:**
  - Python: Enforce PEP 8 style formatting.
  - JavaScript: Enforce Prettier formatting configurations.
- **Testing Philosophy:** Validate logic using standard frameworks (e.g., `pytest` on backend, React Testing Library on frontend). Run unit tests for core modules, and integration tests for critical database and API path lifecycles.
- **Git Commit Style:** Use the Conventional Commits structure (`type(scope): description`). Examples: `feat(api): add live alert monitoring endpoints`, `fix(db): correct database migration coordinate check`.

---

# Constraints

- **Zero Budget Infrastructure:** The entire solution must deploy and run successfully within the free tiers of Render, Supabase, and Vercel.
- **Open-Source Priority:** Give precedence to open-source developer libraries, mapping clients, and frameworks over paid SaaS products or restricted APIs.
- **Production-Ready Modular Monolith:** The project intentionally follows a Production-Ready Modular Monolith architecture instead of Microservices to maximize maintainability, interview clarity, deployment simplicity and development speed.
- **Complexity Minimization:** Reject features that do not directly improve real-time situational awareness or recruiter impact.
- **Recruiter Impact Focus:** Prioritize visually impressive geospatial interactions, clean and well-structured APIs, fully written test cases, and clear technical descriptions.
- **Purpose-Driven Technology Selection:** Every technology introduced must solve a real engineering problem. Resume-driven complexity and unnecessary technology additions are intentionally avoided.

---

# Success Criteria

The "Project Complete" status is achieved when the platform satisfies the following:
1. **Production Deployment:** The frontend and backend run on production platforms with a live PostgreSQL database and Supabase Auth.
2. **End-to-End Integration:** The React frontend displays dynamic incidents, historical data, and analysis summaries retrieved from backend API endpoints.
3. **Comprehensive Coverage:** Core backend routines (predictions, alerts acknowledgment, report generation, system status) are fully operational.
4. **Verifiable Test Suites:** Code includes unit and integration tests with clear execution instructions in README files.
5. **Interview Ready:** The repository stands out to engineering recruiters by demonstrating clean code, architectural specifications, and modern DevOps practices. Every implemented feature should be production-ready, fully testable, deployable, and explainable in technical interviews from both architectural and implementation perspectives.
6. **Self-Documenting Sandbox:** Anyone can clone the repository, run a simple startup command, and seed realistic demo data in under 5 minutes.

---

# Future Roadmap

## Phase 1: Real-Time Weather Integration

## Phase 2: Vector Search and RAG

## Phase 3: Model Ingestion and ONNX

## Phase 4: Observability and Performance Hardening
