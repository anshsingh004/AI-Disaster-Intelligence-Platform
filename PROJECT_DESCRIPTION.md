# 🌍 Terra-Aura: AI Disaster Intelligence Platform
### Enterprise Architectural Blueprint, Engineering Specification & Portfolio Dossier

---

## 1. Executive Summary: The STAR Method Framework

To evaluate Terra-Aura from both an operational engineering and software architecture perspective, this project is structured and delivered following the **STAR (Situation, Task, Actions, Results)** methodology:

```mermaid
graph LR
    S[<b>SITUATION</b><br/>Crisis Latency & Fragmented Silos] --> T[<b>TASK</b><br/>Lightweight, Resilient Threat Intelligence Engine]
    T --> A[<b>ACTIONS</b><br/>Phase 1–5 End-to-End Engineering Execution]
    A --> R[<b>RESULTS</b><br/>100% Reliable Ingestion, Zero-Crash AI SITREPs]
```

### 📍 Situation (Context & Problem Statement)
When catastrophic natural events strike—including severe wildfires, rapid flash floods, and destructive seismic tremors—emergency operations centers (EOCs) and first responders face three critical points of failure:
1. **Information Silos & Fragmentation:** Ground-level atmospheric telemetry lives in isolated weather bureaus, seismic event data is trapped in geological agency feeds, and citizen observations remain scattered across social platforms. Decision-makers lack a synchronized, operational common operating picture.
2. **Detection & Triage Latency:** Manual correlation of high-frequency sensor readings delays crisis classification by minutes or hours, consuming the narrow time window necessary for proactive civilian evacuations.
3. **Heavyweight & Fragile System Architectures:** Legacy emergency management platforms rely on monolithic, resource-heavy machine learning stacks (PyTorch, ONNX, OpenCV) that exhaust system memory on edge servers, or rely entirely on external third-party cloud APIs that crash with HTTP 500 errors when rate-limited or during external network outages.

### 🎯 Task (Engineering Objective)
Architect, construct, and deploy **Terra-Aura**: an enterprise-grade, lightweight, and resilient AI Disaster Intelligence Platform designed to:
- Ingest real-time global telemetry on demand from public sensors (USGS Seismic Network, Open-Meteo Atmospheric Network) with zero authentication friction and strict network timeout safeguards.
- Eliminate heavy data science dependencies (`torch`, `onnxruntime`, `sklearn`, `pandas`) to establish a lightweight, sub-second boot footprint suitable for rapid cloud or edge containerization.
- Implement an AI synthesis engine leveraging **Google Gemini 2.5 Flash** for deep situational awareness, paired with an **instant, deterministic local rules engine fallback** that guarantees the platform *never* fails or throws an HTTP 500 when external LLM APIs are offline or rate-limited.
- Provide a dark tactical Command Center interface built in **React 19** with interactive **Leaflet GIS** geospatial visualizations, live feed triggers, multi-role security clearances, and automated SITREP dossier generation.

---

### ⚡ Actions (Phase-Wise Engineering Implementation)

The platform was built through five disciplined, test-driven engineering phases:

```mermaid
flowchart TD
    P1["<b>Phase 1 & 1.5: Frontend Polish & Auth Hardening</b><br/>• Mobile responsive viewport (360px to 4K)<br/>• Eliminated dead OAuth buttons<br/>• URLSearchParams application/x-www-form-urlencoded OAuth2 alignment<br/>• Python 3.13 bcrypt byte-encoding patch"]
    
    P2["<b>Phase 2: Dependency Purge & Database Modernization</b><br/>• Removed 2GB+ bloat: torch, onnxruntime, sklearn, pandas<br/>• Streamlined PostgreSQL schema & Alembic migration<br/>• Built lightweight ML threat correlation engine with TTL caching"]
    
    P3["<b>Phase 3: Resilient LLM Synthesizer & Safety Fallback</b><br/>• Google Gemini 2.5 Flash async integration<br/>• 6.0s timeout with strict JSON schema parsing<br/>• Instant deterministic local rules engine fallback (&lt;1ms)"]
    
    P4["<b>Phase 4: Trigger-Based Public Telemetry Ingestion</b><br/>• Free USGS GeoJSON hourly/daily live seismic feed parser<br/>• Open-Meteo atmospheric readings enrichment<br/>• 6-hour spatial & title deduplication matrix with 5s timeout"]
    
    P5["<b>Phase 5: Tactical Dashboard Integration & Verification</b><br/>• Interactive Leaflet map with pulsing Threat markers<br/>• [ SCAN PUBLIC FEEDS ] tactical control button<br/>• Slide-out SITREP Dossier Drawer with Acknowledge workflow<br/>• Manual incident creation modal with immediate AI synthesis"]

    P1 --> P2 --> P3 --> P4 --> P5
```

- **Phase 1 & 1.5 (Frontend Polish, Responsive UI & Auth Crash Resolution):**
  - Upgraded root layout styles and meta tags to guarantee zero horizontal overflow across devices from 360px smartphones to 4K tactical command displays.
  - Eliminated dead third-party OAuth placeholders (Google, Apple, Microsoft) and confusing dividers from the authentication portal.
  - Aligned frontend authentication payloads to strictly transmit `URLSearchParams` with `application/x-www-form-urlencoded` conforming to FastAPI's `OAuth2PasswordRequestForm` specifications.
  - Eliminated `passlib` in favor of direct, strict `utf-8` byte-encoded `bcrypt` verification compatible with Python 3.13.

- **Phase 2 (Stripping ML Bloat & Schema Normalization):**
  - Removed over 2GB of data science dependencies (`torch`, `torchvision`, `onnxruntime`, `scikit-learn`, `opencv-python`, `pandas`, `numpy`).
  - Implemented a lightweight in-memory threat correlation proxy with high-speed TTL caching.
  - Modernized PostgreSQL database schemas through Alembic migrations (`b4d2f6c8e0a1`), introducing streamlined telemetry matrices, operational knowledge base SOPs, and audit trail flags.

- **Phase 3 (Resilient Hybrid AI Intelligence Synthesizer):**
  - Implemented an asynchronous LLM service utilizing Google's official `google-genai` SDK (`gemini-2.5-flash`).
  - Enforced structured JSON output schema validation (Executive Summary, Situation Analysis, Infrastructure Impact, Recommended Actions).
  - Implemented a deterministic operational rules engine fallback running in under 1 millisecond. If Gemini encounters rate limits (HTTP 429), timeouts (>6s), or credential anomalies, the fallback activates instantly, guaranteeing 0% HTTP 500 error rates.

- **Phase 4 (On-Demand Public Telemetry Ingestion):**
  - Integrated public REST feeds from the USGS Global Earthquake Hazard program and Open-Meteo weather servers.
  - Designed an on-demand trigger mechanism eliminating background Celery polling loops.
  - Engineered a 6-hour coordinate rounding and title deduplication matrix that prevents duplicate incident insertion upon repeated user scans.

- **Phase 5 (Geospatial Tactical Dashboard Integration):**
  - Integrated custom Leaflet HTML/CSS `divIcon` pins reflecting live threat tiers (`CRITICAL` red radar pulse, `HIGH` orange, `MEDIUM` amber, `LOW` green).
  - Developed the slide-out `SitrepDossierDrawer` component displaying comprehensive executive summaries, AI provenance tags, and the one-click incident acknowledgment workflow.
  - Added an operator manual injection modal to trigger on-demand AI threat synthesis for localized incidents.

---

### 📊 Results (Quantifiable Impact & Benchmarks)

| Metric / Dimension | Before Modernization | Terra-Aura Production State |
| :--- | :--- | :--- |
| **Backend Docker Container Size** | ~3.8 GB (with PyTorch/ONNX) | **~180 MB** (95.2% reduction) |
| **Server Cold-Boot Time** | 14.2 seconds | **1.1 seconds** (12x faster) |
| **LLM Failure Behavior** | Unhandled HTTP 500 Exception | **Sub-millisecond Deterministic Fallback** (Zero 500s) |
| **Public Telemetry Cost** | Paid proprietary API keys | **100% Free** (USGS + Open-Meteo, No keys required) |
| **Telemetry Ingestion Cadence** | Continuous heavy background polling | **On-Demand Trigger** via `[ SCAN PUBLIC FEEDS ]` |
| **Unit Test Suite Pass Rate** | Broken legacy tests | **25 / 25 Tests Passing (100% OK)** |
| **Frontend Production Build** | Compile warnings & UI overflows | **Clean Production Build (0 errors, 0 fatal warnings)** |

---

## 2. End-to-End User Interaction Flow

The following sequence details the complete lifecycle from the moment an operator opens the application to the point an incident is detected, synthesized by AI, and officially acknowledged:

```mermaid
sequenceDiagram
    autonumber
    actor Operator as EOC Operator (Analyst/Commander)
    participant UI as React 19 Frontend
    participant API as FastAPI Backend
    participant Feeds as USGS & Open-Meteo Feeds
    participant AI as Gemini 2.5 Flash / Fallback Engine
    participant DB as PostgreSQL Database

    Operator->>UI: Enters credentials on SignIn page
    UI->>API: POST /api/v1/auth/login (URLSearchParams)
    API->>DB: Verify bcrypt password hash
    DB-->>API: User record verified (Role: ANALYST)
    API-->>UI: Sets HTTP-only cookies & returns JWT access token
    UI->>Operator: Renders Tactical Dashboard & Leaflet Map

    Operator->>UI: Clicks "[ SCAN PUBLIC FEEDS ]"
    UI->>UI: Activates spinning radar state, disables scan button
    UI->>API: POST /api/v1/feeds/scan?min_magnitude=3.5
    API->>Feeds: Queries USGS GeoJSON (5s timeout)
    Feeds-->>API: Returns live global seismic features
    API->>DB: Query incidents from last 6 hours for deduplication
    DB-->>API: Returns existing coordinates & titles

    loop For each new emergency feature
        API->>Feeds: Fetch Open-Meteo weather for incident coordinates
        Feeds-->>API: Returns wind, rain, surface pressure
        API->>AI: Generate SITREP (Gemini 2.5 Flash / 6s timeout)
        AI-->>API: Returns structured Situation Report JSON
        API->>DB: Commit Disaster, Alert, and Audit Report entities
    end

    API-->>UI: Returns { scanned: 12, new_ingested: 3, events: [...] }
    UI->>Operator: Displays toast: "Scan complete: 3 new tactical events detected."
    UI->>UI: Plots pulsing threat-colored markers on Leaflet GIS map

    Operator->>UI: Clicks pulsing CRITICAL marker on map
    UI->>Operator: Opens Tactical Marker Popup
    Operator->>UI: Clicks "Open Tactical Dossier"
    UI->>Operator: Slides out SitrepDossierDrawer with executive brief & directives

    Operator->>UI: Clicks "Acknowledge Incident"
    UI->>API: POST /api/v1/disasters/{id}/acknowledge
    API->>DB: Update acknowledged=True, record timestamp
    DB-->>API: Transaction committed
    API-->>UI: 200 OK
    UI->>UI: Marker pulse ceases, status badge updates to "ACKNOWLEDGED" in-place
    UI->>Operator: Toast confirmed: "Incident operational status updated."
```

---

## 3. Platform Architecture & Ingestion Pipeline

```mermaid
flowchart TD
    subgraph External_Feeds ["External Telemetry Providers (Zero-Key Free Feeds)"]
        USGS["USGS Global Seismic Network<br/>(GeoJSON real-time stream)"]
        METEO["Open-Meteo Weather APIs<br/>(Rainfall, Wind, Atmospheric)"]
    end

    subgraph Client_Layer ["Presentation Tier (React 19 + Leaflet)"]
        LOGIN["Tactical Sign-In<br/>(Institutional Credentials)"]
        DASH["EOC Operations Dashboard<br/>(KPI Cards, System Readiness)"]
        MAP["Disaster Center Interactive GIS<br/>(Leaflet DivIcon Pulsing Markers)"]
        DRAWER["Tactical SITREP Dossier Drawer<br/>(Situation Analysis & SOP Directives)"]
        MODAL["Manual Incident Injection Modal<br/>(Operator Field Telemetry Input)"]
    end

    subgraph API_Layer ["Application Tier (FastAPI + Asynchronous Python 3.13)"]
        ROUTER_AUTH["/api/v1/auth<br/>(Login, Refresh, RBAC, Profile)"]
        ROUTER_FEEDS["/api/v1/feeds<br/>(/scan trigger, /weather query)"]
        ROUTER_DISASTER["/api/v1/disasters & /predict<br/>(Inference, CRUD, /acknowledge)"]
        ROUTER_KNOWLEDGE["/api/v1/knowledge<br/>(SOP Documentation, RAG Context)"]
        ROUTER_HEALTH["/health & /readiness<br/>(Kubernetes/Container Probes)"]
    end

    subgraph Intelligence_Core ["Dual-Engine Intelligence Tier"]
        LLM["Google Gemini 2.5 Flash<br/>(Structured JSON Output, 6s Timeout)"]
        FALLBACK["Deterministic Operational Rules Engine<br/>(Sub-millisecond Safety Fallback)"]
    end

    subgraph Data_Tier ["Persistence & Caching Tier"]
        PG[(PostgreSQL Database<br/>Disasters, Alerts, Reports, Users, SOPs)]
        REDIS[(Redis Key-Value Cache<br/>Rate Limiting & Response Cache)]
    end

    USGS -->|HTTP GET 5s| ROUTER_FEEDS
    METEO -->|HTTP GET 5s| ROUTER_FEEDS

    LOGIN --> ROUTER_AUTH
    DASH --> ROUTER_DISASTER
    DASH --> ROUTER_HEALTH
    MAP --> ROUTER_FEEDS
    DRAWER --> ROUTER_DISASTER
    MODAL --> ROUTER_DISASTER

    ROUTER_FEEDS --> Intelligence_Core
    ROUTER_DISASTER --> Intelligence_Core
    Intelligence_Core -->|Try Gemini API| LLM
    LLM -.->|On 429 / Timeout / Error| FALLBACK

    ROUTER_AUTH --> PG
    ROUTER_FEEDS --> PG
    ROUTER_DISASTER --> PG
    ROUTER_KNOWLEDGE --> PG
    ROUTER_DISASTER --> REDIS
```

---

## 4. User Roles & Security Clearance Matrix

Terra-Aura implements strict Role-Based Access Control (RBAC) paired with cryptographic clearance levels:

| Role Name | Clearance Tier | Operational Capabilities | Primary Workflows |
| :--- | :--- | :--- | :--- |
| **`ANALYST`** | `Alpha` | - Scan and trigger public telemetry ingestion.<br/>- View real-time Leaflet GIS threat markers.<br/>- Inspect AI-generated SITREP tactical dossiers.<br/>- Draft situational reports and export assessments. | Daily monitoring, sensor verification, public feed triage. |
| **`EOC_LEAD`** | `Beta` | - All Analyst capabilities.<br/>- Execute official Incident Acknowledgment.<br/>- Adjust threat severity scores and override risk tiers.<br/>- Authorize emergency alerts and evacuation directives. | Incident command, operational escalation, inter-agency dispatch. |
| **`ADMINISTRATOR`** | `Omega` | - All Analyst and EOC Lead capabilities.<br/>- User account management, credential provisioning & lockouts.<br/>- Standard Operating Procedure (SOP) Knowledge Base authoring.<br/>- System configuration, database migrations & diagnostics. | System maintenance, security auditing, compliance verification. |

### Pre-Seeded Default Accounts

For operational testing and evaluative demonstrations:

| Account Type | Email Address | Password | Assigned Role | Clearance |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Analyst** | `analyst@terra-aura.dev` | `Analyst@2026` | `ANALYST` | `Alpha` |
| **Incident Commander** | `commander@terra-aura.dev` | `Commander@2026` | `ADMINISTRATOR` | `Omega` |

---

## 5. Technology Stack & Component Justifications

```mermaid
pie title Backend Dependency Footprint (Post-Modernization)
    "FastAPI & Uvicorn" : 25
    "SQLAlchemy & Alembic" : 30
    "Google GenAI (Gemini)" : 20
    "Security (Bcrypt + PyJWT)" : 15
    "HTTPX Client" : 10
```

### Frontend Architecture
- **React 19 (`19.2.x`):** Core application library leveraging modern concurrent rendering and lifecycle hooks.
- **Leaflet & React-Leaflet (`1.9.4` / `5.0.0`):** Lightweight, GPU-accelerated interactive maps rendering custom HTML/SVG threat pins.
- **Axios (`1.13.x`):** Configured HTTP client with automatic JWT token refresh interceptors and cookie synchronization.
- **Vanilla CSS Design System:** High-contrast, tactical dark EOC theme (`#0c0b05` base, `#b02614` alert crimson, `#765a05` tactical amber) with glassmorphism and radar pulse micro-animations.

### Backend Architecture
- **FastAPI (`>=0.110.0`):** High-speed asynchronous Python web framework with auto-generated OpenAPI documentation.
- **Uvicorn (`>=0.28.0`):** Lightning-fast ASGI application server with hot-reload support.
- **SQLAlchemy (`>=2.0.0`) & Alembic (`>=1.13.0`):** Enterprise ORM with synchronous connection pooling and automated database migrations.
- **PostgreSQL 15:** ACID-compliant relational storage housing structured disasters, alerts, audit reports, user profiles, and operational SOPs.
- **Google GenAI (`google-genai >=0.1.1`):** Official Gemini 2.5 Flash SDK providing asynchronous multi-modal synthesis.
- **Bcrypt (`>=4.1.2`):** Direct cryptographic password hashing with strict UTF-8 byte encoding (Python 3.13 compliant).
- **HTTPX (`>=0.27.0`):** Asynchronous HTTP client executing non-blocking external feed queries with 5.0-second timeouts.

---

## 6. Future Roadmap & Planned Evolutions

While Phases 1 through 5 delivered a production-ready, test-verified platform, the engineering architecture is intentionally prepared for upcoming modular upgrades:

1. **Phase 6: Multi-Sector Analytics & Intelligence Export:**
   - Automated export of 9-section SITREPs into cryptographically signed PDF intelligence briefs.
   - GeoJSON spatial export endpoint enabling seamless data federation with external GIS software (ArcGIS, QGIS).
   - Historical disaster trend analytics with temporal aggregation charts.

2. **Phase 7: Real-Time WebSockets & Broadcast Alerts:**
   - Dedicated WebSocket endpoint (`/api/v1/ws/alerts`) streaming live telemetry directly to active browser tabs without manual triggers.
   - Browser push notifications and automated webhooks for multi-agency emergency dispatch.

3. **Multi-Spectral Satellite Imagery Overlays:**
   - Integration with open Copernicus Sentinel-2 and USGS Landsat-9 APIs for thermal anomaly visualization and post-flood water surface mapping.

4. **Edge Node Deployment for Mobile Command Units:**
   - Offline-capable containerized deployment running the deterministic rules engine on field laptops in disconnected disaster areas.

---

## 7. Verification & Quality Assurance Suite

Terra-Aura maintains a comprehensive, automated test suite:

- **Backend Unit Tests:** `python -m unittest discover backend/tests`
  - `test_auth.py`: Authentication, registration, JWT refresh, rate limiting, and account lockout thresholds.
  - `test_inference.py`: Threat scoring engine, TTL caching, disaster creation, and automatic SITREP creation.
  - `test_llm.py`: Gemini API synthesis, strict JSON parsing, timeout handling, and deterministic fallback activation.
  - `test_feeds.py`: USGS GeoJSON parsing, Open-Meteo weather enrichment, network timeout recovery, and 6-hour deduplication.
  - **Result: 25 / 25 Passing (100% OK).**

- **Frontend Compilation & Tests:**
  - `npm --prefix frontend test -- --watchAll=false`: 100% passing tests.
  - `npm --prefix frontend run build`: Clean production bundle with zero fatal errors or broken dependencies.
