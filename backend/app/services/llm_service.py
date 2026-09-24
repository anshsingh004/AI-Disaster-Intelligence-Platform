import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Google GenAI client safely from settings or environment
def _resolve_gemini_api_key() -> Optional[str]:
    return os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)

api_key = _resolve_gemini_api_key()
client = genai.Client(api_key=api_key) if api_key else None


def get_genai_client() -> Optional[genai.Client]:
    """
    Dynamically retrieve or reinitialize the Google GenAI client if the
    GEMINI_API_KEY environment variable is updated at runtime.
    """
    global client
    current_key = _resolve_gemini_api_key()
    if current_key:
        if client is None or getattr(client, "_api_key", None) != current_key:
            try:
                client = genai.Client(api_key=current_key)
            except Exception as e:
                logger.warning(f"Failed to instantiate Google GenAI Client: {e}")
                client = None
    else:
        client = None
    return client


def deterministic_fallback_sitrep(telemetry_data: Optional[Dict[str, Any]], incident_type: str) -> Dict[str, Any]:
    """
    Local deterministic operational rules engine.
    Inspects telemetry values without any external network calls and generates
    a fully conformant Situation Report (SITREP) in sub-millisecond time.
    """
    telemetry = telemetry_data or {}

    def _extract_float(keys: List[str], default: float = 0.0) -> float:
        for k in keys:
            val = telemetry.get(k)
            if val is not None:
                try:
                    return float(val)
                except (ValueError, TypeError):
                    continue
        return default

    rainfall = _extract_float(["rainfall", "weather_rainfall", "rainfall_mm", "precipitation"])
    wind_speed = _extract_float(["wind_speed", "weather_wind_speed", "wind_kmh", "gust"])
    seismic_magnitude = _extract_float(["seismic_magnitude", "magnitude", "earthquake_magnitude", "richter"])
    social_score = _extract_float(["social_score", "social_signal_score", "citizen_reports"])

    # If earthquake incident without direct seismograph, infer magnitude estimate from social intensity
    if incident_type.lower() == "earthquake" and seismic_magnitude == 0.0:
        if social_score >= 0.8:
            seismic_magnitude = 6.2
        elif social_score >= 0.5:
            seismic_magnitude = 4.8
        elif social_score > 0.0:
            seismic_magnitude = 3.2

    # Deterministic Operational Rules Matrix
    if rainfall > 70.0 or wind_speed > 100.0 or seismic_magnitude >= 6.0:
        risk_level = "CRITICAL"
        actions = [
            "Issue immediate mandatory evacuation orders",
            "Mobilize disaster response teams to sector",
            "Establish temporary emergency shelters"
        ]
        infra_impact = "Severe structural hazards across low-lying transport corridors, bridges, and municipal power grids."
    elif rainfall > 35.0 or wind_speed > 60.0 or seismic_magnitude >= 4.5:
        risk_level = "HIGH"
        actions = [
            "Deploy emergency warning alerts to residents",
            "Place hospital trauma wards on standby",
            "Inspect arterial drainage and bridge infrastructure"
        ]
        infra_impact = "Moderate disruption to primary transit routes, stormwater conduits, and above-ground utility lines."
    elif rainfall > 15.0 or wind_speed > 40.0 or seismic_magnitude >= 3.0:
        risk_level = "MEDIUM"
        actions = [
            "Monitor localized waterlogging",
            "Alert municipal road maintenance crews"
        ]
        infra_impact = "Localized drainage congestion and ponding on secondary roadways; primary transit networks operational."
    else:
        risk_level = "LOW"
        actions = [
            "Continue routine sensor telemetry polling"
        ]
        infra_impact = "Nominal conditions across critical infrastructure; no operational disruptions detected."

    inc_label = incident_type.replace("_", " ").strip().title() or "Hazard"
    executive_summary = (
        f"Tactical assessment for {inc_label} incident indicates {risk_level} threat level based on sensor telemetry. "
        f"Emergency operations personnel should execute standard {risk_level.lower()} tactical directives."
    )
    situation_analysis = (
        f"Automated sensor analysis detected rainfall rate of {rainfall:.1f} mm/hr, sustained wind speeds of "
        f"{wind_speed:.1f} km/h, and seismic telemetry at {seismic_magnitude:.1f} magnitude. "
        f"Atmospheric and geophysical indicators conform to {risk_level} operational threshold."
    )

    return {
        "risk_level": risk_level,
        "executive_summary": executive_summary,
        "situation_analysis": situation_analysis,
        "infrastructure_impact": infra_impact,
        "recommended_actions": actions,
        "ai_confidence_note": "Generated via Deterministic Operational Rules Engine (Fallback Mode)."
    }


async def generate_incident_sitrep(
    telemetry_data: Optional[Dict[str, Any]],
    incident_type: str,
    context_notes: str = ""
) -> Dict[str, Any]:
    """
    Generates a structured Situation Report (SITREP) using Google Gemini 2.5 Flash,
    paired with an immediate deterministic fallback if the API is offline, invalid,
    rate-limited, or times out (>6 seconds).
    
    GUARANTEE: Under no circumstance will this function raise an unhandled exception
    or block backend event loops.
    """
    active_client = get_genai_client()

    # Instant local fallback if API key is not configured or client failed to instantiate
    if active_client is None:
        return deterministic_fallback_sitrep(telemetry_data, incident_type)

    prompt = (
        f"Incident Classification: {incident_type}\n"
        f"Real-Time Telemetry: {json.dumps(telemetry_data or {})}\n"
        f"Operational Context: {context_notes or 'Standard monitoring sector'}\n\n"
        "Generate a structured Situation Report (SITREP) adhering strictly to this JSON schema:\n"
        "{\n"
        '  "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",\n'
        '  "executive_summary": "Concise 2-sentence tactical summary",\n'
        '  "situation_analysis": "Detailed ground situation assessment",\n'
        '  "infrastructure_impact": "Identified risks to utilities, roads, shelters",\n'
        '  "recommended_actions": ["Direct action item 1", "Direct action item 2", "Direct action item 3"],\n'
        '  "ai_confidence_note": "Assessment note generated via Gemini 2.5 Flash"\n'
        "}"
    )

    try:
        config = types.GenerateContentConfig(
            system_instruction=(
                "You are an Emergency Operations Center (EOC) Intelligence Director. "
                "Your objective is to evaluate multi-modal disaster telemetry and operational context "
                "to produce a concise, authoritative Situation Report (SITREP) in strict JSON format. "
                "Never output conversational text, markdown formatting, or code fences."
            ),
            response_mime_type="application/json",
            temperature=0.2,
        )

        response = await asyncio.wait_for(
            active_client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config
            ),
            timeout=6.0
        )

        raw_text = response.text.strip() if response and response.text else ""
        if not raw_text:
            raise ValueError("Empty response received from Gemini API")

        # Strip any code block fences if present despite JSON mime-type
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_text = "\n".join(lines).strip()

        parsed = json.loads(raw_text)

        # Enforce required schema keys
        required_keys = [
            "risk_level",
            "executive_summary",
            "situation_analysis",
            "infrastructure_impact",
            "recommended_actions"
        ]
        for key in required_keys:
            if key not in parsed or not parsed[key]:
                raise ValueError(f"Missing or empty required SITREP key: {key}")

        # Validate types and normalize values
        if not isinstance(parsed["recommended_actions"], list):
            if isinstance(parsed["recommended_actions"], str):
                parsed["recommended_actions"] = [parsed["recommended_actions"]]
            else:
                raise ValueError("recommended_actions must be an array of strings")

        if parsed["risk_level"].upper() not in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
            parsed["risk_level"] = "HIGH"
        else:
            parsed["risk_level"] = parsed["risk_level"].upper()

        if not parsed.get("ai_confidence_note"):
            parsed["ai_confidence_note"] = "Assessment note generated via Gemini 2.5 Flash"

        return parsed

    except asyncio.TimeoutError:
        logger.warning("Gemini SITREP synthesis timed out after 6.0s. Falling back to deterministic rules.")
        return deterministic_fallback_sitrep(telemetry_data, incident_type)
    except Exception as e:
        logger.warning(f"Gemini SITREP synthesis error ({type(e).__name__}: {e}). Executing deterministic fallback.")
        return deterministic_fallback_sitrep(telemetry_data, incident_type)


def generate_incident_sitrep_sync(
    telemetry_data: Optional[Dict[str, Any]],
    incident_type: str,
    context_notes: str = ""
) -> Dict[str, Any]:
    """
    Synchronous execution wrapper for generate_incident_sitrep with hardcoded safety fallback.
    Safely handles both active event loop contexts and standalone script executions.
    """
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    asyncio.run,
                    generate_incident_sitrep(telemetry_data, incident_type, context_notes)
                )
                return future.result(timeout=7.0)
        else:
            return loop.run_until_complete(
                generate_incident_sitrep(telemetry_data, incident_type, context_notes)
            )
    except Exception as e:
        logger.warning(f"Synchronous SITREP runner error ({e}). Returning deterministic fallback.")
        return deterministic_fallback_sitrep(telemetry_data, incident_type)
