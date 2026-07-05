 # Terra-Aura Backend Design

This backend design is matched to the current frontend pages in `frontend/src`: Sign In, Dashboard, Disaster Center, Analytics, Reports, Profile, Legal, Support, System Status, and Backend Pending.

## Goal

Build a free, deployable, recruiter-friendly backend that makes the frontend feel like a real 2026-2027 disaster intelligence platform without becoming too difficult to implement.

The backend should:

- Replace static dashboard data with API data.
- Support Google, Microsoft/Outlook, Apple, and email sign-in through a managed auth provider.
- Power one-click actions instead of requiring users to manually call routes.
- Store disaster incidents, reports, support tickets, alerts, profile settings, and audit logs.
- Call free weather APIs for real environmental signals.
- Return AI-style explanations from the existing rule-based ML layer first, with room for scikit-learn or Hugging Face later.
- Deploy for free using Vercel, Render, and Supabase.

## Recommended Free Stack

- Backend API: FastAPI
- Database: Supabase Postgres
- Auth: Supabase Auth
- Weather data: Open-Meteo
- ORM: SQLAlchemy
- Migrations: Alembic
- Validation: Pydantic
- Deployment: Render free web service
- Frontend deployment: Vercel

Supabase Auth is the simplest fit because the frontend already has social sign-in buttons. Use Supabase for Google, Microsoft Azure/Outlook, Apple, and email sign-in. The backend should verify Supabase JWTs instead of building OAuth from scratch.

## Backend Folder Structure

```txt
backend/
  app/
    main.py
    db.py
    core/
      config.py
      security.py
      errors.py
    models/
      disaster.py
      alert.py
      report.py
      support_ticket.py
      user_profile.py
      audit_log.py
    schemas/
      disaster.py
      alert.py
      report.py
      dashboard.py
      analytics.py
      support.py
      user_profile.py
      system_status.py
      auth.py
    routers/
      health.py
      auth.py
      dashboard.py
      disasters.py
      alerts.py
      analytics.py
      reports.py
      weather.py
      support.py
      profile.py
      system_status.py
      demo.py
    services/
      prediction_service.py
      disaster_service.py
      weather_service.py
      analytics_service.py
      report_service.py
      support_service.py
      profile_service.py
      status_service.py
      audit_service.py
    migrations/
  .env.example
  requirements.txt
```

## Frontend Page To Backend Mapping

### Sign In

Frontend file: `frontend/src/pages/SignIn.js`

Current buttons:

- Continue with Google
- Continue with Apple
- Sign in with email

Backend/API support:

- Supabase handles the actual OAuth flow on the frontend.
- FastAPI verifies the Supabase JWT for protected routes.
- Add Microsoft/Outlook in the UI later because the original requirement asks for Gmail or Outlook sign-in.

Endpoints:

```txt
GET /auth/me
POST /auth/sync-profile
POST /auth/logout-audit
```

`GET /auth/me` response:

```json
{
  "id": "uuid",
  "name": "Google User",
  "email": "user@gmail.com",
  "provider": "google",
  "role": "Lead Geospatial Analyst",
  "clearance_level": "Alpha"
}
```

### Dashboard

Frontend file: `frontend/src/pages/Dashboard.js`

Current static areas:

- Active Incidents
- Active Incidents KPI
- AI Confidence KPI
- Sectors Monitored KPI
- Response Rate KPI
- Quick Actions
- System Status

Endpoints:

```txt
GET /dashboard/summary
GET /incidents/active
GET /system/status
POST /demo/seed
```

`GET /dashboard/summary` response:

```json
{
  "active_incidents": 124,
  "ai_confidence": 94,
  "sectors_monitored": 47,
  "response_rate": 92,
  "deltas": {
    "active_incidents": "+3 today",
    "ai_confidence": "+5% this week",
    "response_rate": "+2% efficiency"
  }
}
```

`GET /incidents/active` response:

```json
[
  {
    "id": 1,
    "type": "Wildfire",
    "sector": "Sector 7G",
    "severity": 94,
    "level": "critical",
    "icon": "local_fire_department",
    "latitude": 28.6139,
    "longitude": 77.209,
    "status": "active",
    "created_at": "2026-06-17T10:30:00Z"
  }
]
```

### Disaster Center

Frontend file: `frontend/src/pages/DisasterCenter.js`

Current static areas:

- Live Sync Active
- Sector label
- New Incident
- Satellite Overlay
- Broadcast Alert
- Search
- Notifications
- Map controls
- Alert pins
- AI Analysis
- Alert tabs
- View Details
- Acknowledge
- Contextual Data
- Escalation Probability

Endpoints:

```txt
GET /alerts/live
GET /alerts/{alert_id}
POST /alerts/{alert_id}/acknowledge
POST /incidents
POST /alerts/broadcast
GET /weather/context?latitude={lat}&longitude={lng}
GET /satellite/overlay?bbox={bbox}
GET /notifications
GET /search?q={query}
```

Minimum implementation:

- Implement `/alerts/live`.
- Implement `/alerts/{id}/acknowledge`.
- Implement `/incidents`.
- Keep `/satellite/overlay` as a mocked metadata endpoint for now, not real satellite imagery.

`GET /alerts/live` response:

```json
[
  {
    "id": 1,
    "level": "critical",
    "title": "Unidentified Thermal Signature, Sector 4",
    "time_label": "2 mins ago",
    "description": "Predictive models indicate a 94% probability of rapid expansion.",
    "escalation_probability": 87,
    "latitude": 28.6139,
    "longitude": 77.209,
    "context_data": [
      {
        "icon": "air",
        "title": "Wind Shear Anomaly",
        "description": "Local wind patterns shifted 45 degrees in the last hour."
      }
    ],
    "acknowledged": false
  }
]
```

### Analytics

Frontend file: `frontend/src/pages/Analytics.js`

Current static areas:

- Avg Confidence
- Response Efficiency
- Regional Stability Index
- Active Incidents
- Severity Trends Over Time
- Type Frequency
- Risk Distribution by Sector
- Data Export
- Full Report

Endpoints:

```txt
GET /analytics/overview
GET /analytics/severity-trends?months=6
GET /analytics/type-frequency
GET /analytics/sector-risk
GET /analytics/export.csv
```

`GET /analytics/overview` response:

```json
{
  "avg_confidence": 85,
  "response_efficiency": 92,
  "regional_stability_index": 0.75,
  "active_incidents": 124
}
```

### Reports

Frontend file: `frontend/src/pages/Reports.js`

Current static areas:

- Generate New Report
- Search reports
- Type filter
- Risk filter
- Last 30 Days
- Reports table
- View report
- Pagination
- Generate report modal
- Footer links

Endpoints:

```txt
GET /reports
GET /reports/{report_id}
POST /reports/generate
GET /reports/{report_id}/download
GET /reports/export.csv
```

Supported filters:

```txt
/reports?query=flood&type=Flood&risk=high&status=active&days=30&page=1&page_size=10
```

`GET /reports` response:

```json
{
  "items": [
    {
      "id": "RPT-8492",
      "type": "Wildfire",
      "icon": "local_fire_department",
      "risk": "critical",
      "location": "Sector 7G, Northern Ridge",
      "timestamp": "2026-06-17T14:30:00Z",
      "status": "active"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 124
}
```

`POST /reports/generate` should create a report record from the latest incidents. For the first version, return JSON and generate a text/markdown report. PDF can be added later.

### Profile

Frontend file: `frontend/src/pages/Profile.js`

Current static areas:

- Personal information
- Role
- Background and specialization
- Alert preferences
- Terminate session
- Edit avatar

Endpoints:

```txt
GET /profile/me
PATCH /profile/me
PATCH /profile/me/preferences
POST /profile/avatar
POST /auth/logout-audit
```

Minimum implementation:

- Save name, email, role, specialization, and notification preferences.
- Avatar upload can stay pending or accept a URL only.

### Legal And Support

Frontend files:

- `frontend/src/pages/Legal.js`
- `frontend/src/pages/BackendPending.js`

Endpoints:

```txt
GET /legal/content
POST /support/tickets
GET /support/tickets/me
```

`POST /support/tickets` request:

```json
{
  "email": "user@gmail.com",
  "category": "Data correction",
  "message": "Flood marker appears in the wrong region."
}
```

### System Status

Current placeholder:

- Backend API pending
- Database pending
- AI Models pending
- Auth Services pending

Endpoints:

```txt
GET /health
GET /system/status
```

`GET /system/status` response:

```json
{
  "api": "online",
  "database": "online",
  "ai_models": "online",
  "auth_services": "online",
  "weather_provider": "online",
  "satellite_feed": "mocked",
  "alert_broadcast": "mocked"
}
```

## Database Tables

### disasters

```txt
id
disaster_type
risk_level
severity_score
confidence
population_at_risk
latitude
longitude
location_name
sector
status
weather_snapshot JSON
ai_explanation
model_name
model_version
created_at
updated_at
```

### alerts

```txt
id
disaster_id
level
title
description
escalation_probability
context_data JSON
acknowledged
acknowledged_by
acknowledged_at
created_at
```

### reports

```txt
id
report_code
disaster_id
type
risk
location
status
summary
content JSON
generated_by
created_at
```

### support_tickets

```txt
id
email
category
message
status
created_at
updated_at
```

### user_profiles

```txt
id
auth_user_id
name
email
provider
role
clearance_level
specialization
avatar_url
preferences JSON
created_at
updated_at
```

### audit_logs

```txt
id
user_email
action
entity_type
entity_id
metadata JSON
created_at
```

## One-Week Implementation Plan

### Day 1: Backend cleanup

- Remove startup data deletion from `main.py`.
- Move DB URL to `.env`.
- Add `core/config.py`.
- Add router structure.
- Keep existing prediction working.

### Day 2: Dashboard and incidents

- Implement `/dashboard/summary`.
- Implement `/incidents/active`.
- Seed realistic demo data.
- Replace Dashboard static arrays with API calls.

### Day 3: Disaster Center

- Implement `/alerts/live`.
- Implement `/alerts/{id}/acknowledge`.
- Implement `/incidents`.
- Connect AI panel, alert tabs, map pins, and acknowledge button.

### Day 4: Weather and prediction upgrade

- Implement `/weather/context`.
- Call Open-Meteo.
- Update `/predict/disaster` to return explanation, model name, version, recommended action, and weather snapshot.

### Day 5: Reports and analytics

- Implement `/reports`.
- Implement `/reports/generate`.
- Implement `/analytics/overview`, `/analytics/severity-trends`, `/analytics/type-frequency`, `/analytics/sector-risk`.
- Connect filters and export button.

### Day 6: Auth, profile, support

- Add Supabase Auth frontend integration.
- Add FastAPI JWT verification.
- Implement `/auth/me`.
- Implement `/profile/me`.
- Implement `/support/tickets`.

### Day 7: Deployment polish

- Add `.env.example`.
- Add Render start command.
- Add README backend setup.
- Add screenshots.
- Add API docs screenshots from `/docs`.
- Deploy backend to Render and database/auth to Supabase.

## Priority Order

If time is short, build in this order:

1. `/health`, `/system/status`
2. `/dashboard/summary`, `/incidents/active`
3. `/alerts/live`, `/alerts/{id}/acknowledge`
4. `/predict/disaster`, `/weather/context`
5. `/reports`, `/reports/generate`
6. `/analytics/*`
7. `/support/tickets`
8. Supabase Auth and `/auth/me`
9. `/profile/me`

This order gives the highest visual impact first because it activates the dashboard, status panel, Disaster Center, reports, and AI analysis before deeper account features.

## Recruiter-Friendly Talking Points

- "The frontend never calls raw routes manually; every backend capability is exposed through user-facing workflow buttons."
- "The AI layer is provider-agnostic: rule-based baseline today, scikit-learn or Hugging Face model later."
- "The app uses free production-style services: Supabase Postgres/Auth, Render, Vercel, and Open-Meteo."
- "The backend exposes operational health, model metadata, audit logs, and structured incident reports."
- "The dashboard is designed as an emergency operations tool, not a generic landing page."

## Features To Avoid For Version 1

- Paid LLM APIs
- Real satellite imagery ingestion
- WebSockets
- Kubernetes
- Complex admin roles
- PDF generation with heavy dependencies
- Training ML models inside the deployed backend

Mock these in version 1 with clean APIs and upgrade later.
