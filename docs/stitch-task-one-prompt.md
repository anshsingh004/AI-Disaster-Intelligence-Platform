# Stitch Prompt: AI Disaster Intelligence Platform

Design a production-ready responsive web app interface for an "AI Disaster Intelligence Platform". This is not a marketing landing page. The first screen must be the actual operational dashboard.

Core product goal:
Create a professional disaster intelligence dashboard for portfolio and interview use. The app helps users monitor disaster risk, inspect map-based incidents, trigger backend API workflows with single-click actions, view AI prediction details, and access modern website essentials such as authentication, support, privacy policy, terms, and contact information.

Required screens and sections:
1. Dashboard / Live risk monitoring
   - Interactive map area for disaster markers.
   - Right-side or responsive lower panel with risk summary metrics: total events, high risk, medium risk, low risk.
   - Selected disaster detail panel showing disaster type, risk level, severity score, confidence, coordinates or location, timestamp, and AI explanation.
   - One-click action area with buttons:
     - Check System Health
     - Load Disaster Details
     - Run Risk Prediction
     - Fetch Weather Signal
   - Latest API result panel that can display formatted JSON or readable response data.
   - Incident feed or recent disaster list that updates when data loads.

2. Authentication / Account
   - Sign in with Google.
   - Sign in with Microsoft / Outlook.
   - Signed-in user chip in the header.
   - Sign out state.
   - Clearly design this as OAuth-ready, not username/password-first.

3. Support Center
   - Support request form with email, issue category, message, and submit button.
   - Support email visible.
   - Operations email visible.
   - Short status area for submitted tickets.

4. Privacy Policy
   - Clean legal content layout.
   - Sections for data collected, disaster report data, account data, retention, deletion request, and contact email.

5. Terms and Conditions
   - Clean legal content layout.
   - State that the platform provides decision-support intelligence and users should verify emergency decisions with official authorities.

6. Contact / Address
   - Registered office address.
   - Support email.
   - Operations email.
   - Privacy email.
   - Phone number placeholder.

Interaction model:
- Users should never need to manually type backend routes like /health, /weather, /predict/disaster, or /disasters.
- Every backend feature must be represented as a clear user-facing button or control.
- Every disaster should have a compact summary and a detailed view.
- The dashboard must work well on desktop and mobile web. A separate mobile app is not required.

Navigation:
- Use a practical app shell with sidebar or top navigation.
- Include sections for Dashboard, Account, Support, Privacy, Terms, and Contact.
- Keep navigation obvious and interview-friendly.

Design constraints:
- Do not create a generic SaaS landing page.
- Do not use decorative feature cards as the main experience.
- Prioritize a dense, useful, operations-focused dashboard.
- Leave colors, typography, and final visual style flexible for manual selection.
- The layout should be polished, modern, and suitable for an industry-ready portfolio project.

Backend/API assumptions:
- Base API URL is configurable.
- Expected endpoints:
  - GET /health
  - GET /disasters
  - POST /predict/disaster
  - GET /weather?latitude={lat}&longitude={lng}
  - Optional future endpoints: GET /models, POST /support, POST /auth/oauth/google, POST /auth/oauth/microsoft

Deliverable:
Generate a complete responsive UI design for the web app, including all screens, components, states, and user flows listed above. Do not omit the modern website essentials.
