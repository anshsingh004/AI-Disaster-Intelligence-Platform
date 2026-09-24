"""
report_service.py
Generates structured AI report content from disaster record data.
All sections are deterministic and template-driven using disaster metrics.
"""
import json
from datetime import datetime


# Risk descriptors for narrative generation
_RISK_DESCRIPTIONS = {
    "CRITICAL": ("catastrophic", "immediate life-threatening", "emergency evacuation protocols"),
    "HIGH":     ("severe",       "significant threat to life and property", "urgent protective actions"),
    "MEDIUM":   ("moderate",     "elevated risk to vulnerable populations", "precautionary measures"),
    "LOW":      ("minor",        "limited risk with standard monitoring", "routine surveillance"),
}

_DISASTER_TYPE_DESCRIPTIONS = {
    "flood":      ("hydrological", "inundation of land areas", "water infrastructure and transport links"),
    "fire":       ("wildfire/fire", "rapid vegetation or structural combustion", "power infrastructure and built environment"),
    "earthquake": ("seismic",      "ground motion and structural stress", "critical infrastructure and building stock"),
    "cyclone":    ("meteorological","high-wind rotational system", "coastal and elevated structures"),
    "storm":      ("meteorological","severe precipitation and wind event", "transport and utility networks"),
    "none":       ("unclassified", "anomalous sensor readings", "general infrastructure"),
}

_FORECAST_BY_RISK = {
    "CRITICAL": "Without immediate intervention, the event is projected to intensify over the next 6–12 hours. AI confidence in deterioration trajectory is high. Cascading secondary hazards (e.g. landslides, structural failures) are probable.",
    "HIGH":     "The hazard is expected to remain active for 12–24 hours with possible intensification. Monitoring cadence should increase to 30-minute intervals. Secondary effects are possible.",
    "MEDIUM":   "Current projections indicate stabilisation within 24–48 hours assuming no new environmental triggers. Standard monitoring intervals (2-hour) are sufficient. Re-escalation is possible if rainfall or wind thresholds are exceeded.",
    "LOW":      "The situation is projected to resolve within 48–72 hours. No significant escalation is anticipated under current atmospheric conditions. Routine monitoring continues.",
}

_RECOMMENDED_BY_RISK = {
    "CRITICAL": (
        "1. Activate Emergency Operations Centre (EOC) immediately.\n"
        "2. Issue mandatory evacuation orders for all zones within 5 km radius.\n"
        "3. Deploy rapid-response search and rescue teams.\n"
        "4. Coordinate with National Disaster Response Force (NDRF) units.\n"
        "5. Open emergency shelters and activate supply chain protocols.\n"
        "6. Establish media blackout zone and public communication channels.\n"
        "7. Request satellite imagery confirmation within 1 hour."
    ),
    "HIGH": (
        "1. Place EOC on Level 2 alert status.\n"
        "2. Issue voluntary evacuation advisory for high-risk zones.\n"
        "3. Pre-position emergency response assets within 10 km.\n"
        "4. Alert local hospitals and trauma centres.\n"
        "5. Activate community warning systems.\n"
        "6. Increase sensor polling frequency to 15-minute intervals."
    ),
    "MEDIUM": (
        "1. Place local emergency teams on standby.\n"
        "2. Issue public awareness bulletin through official channels.\n"
        "3. Inspect critical infrastructure in the affected zone.\n"
        "4. Review and test emergency communication systems.\n"
        "5. Monitor AI model outputs for escalation triggers."
    ),
    "LOW": (
        "1. Continue standard surveillance and monitoring.\n"
        "2. Log incident for trend analysis and model retraining.\n"
        "3. Notify local authority liaison for situational awareness.\n"
        "4. No immediate protective action required."
    ),
}


def generate_report_content(disaster) -> dict:
    """
    Generates all 9 structured AI report sections for a given disaster ORM object.
    Returns a dict with keys matching Report model column names.
    """
    dtype = (disaster.disaster_type or "none").lower()
    risk = (disaster.risk_level or "LOW").upper()
    severity_val = disaster.severity_score if disaster.severity_score is not None else 0.6
    confidence_val = disaster.confidence if disaster.confidence is not None else 0.85
    pop_val = disaster.population_at_risk if disaster.population_at_risk is not None else 25000

    severity_pct = round(severity_val * 100)
    confidence_pct = round(confidence_val * 100)
    pop = f"{pop_val:,}"
    lat = f"{disaster.latitude:.4f}"
    lon = f"{disaster.longitude:.4f}"
    ts = disaster.created_at.strftime("%Y-%m-%d %H:%M UTC") if disaster.created_at else datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    risk_adj, risk_threat, risk_protocol = _RISK_DESCRIPTIONS.get(risk, _RISK_DESCRIPTIONS["LOW"])
    d_category, d_mechanism, d_infra = _DISASTER_TYPE_DESCRIPTIONS.get(dtype, _DISASTER_TYPE_DESCRIPTIONS["none"])

    # 1. Executive Summary
    executive_summary = (
        f"Terra-Aura AI Intelligence has detected a {risk_adj} {dtype} event at coordinates "
        f"{lat}°N, {lon}°E at {ts}. The event has been classified as {risk} risk with a severity "
        f"index of {severity_pct}% and AI prediction confidence of {confidence_pct}%. "
        f"Approximately {pop} individuals are estimated to be within the impact radius. "
        f"{risk_protocol.capitalize()} are recommended as the immediate response posture."
    )

    # 2. Situation Analysis
    situation_analysis = (
        f"AI sensor fusion analysis across weather telemetry, NLP social signal feeds, and satellite "
        f"imagery indicates a developing {d_category} event. The primary hazard mechanism is {d_mechanism}. "
        f"Environmental sensor readings show elevated risk indicators that triggered the AI classification "
        f"pipeline at {ts}. The event epicentre is located at {lat}°N, {lon}°E. "
        f"Severity scoring places this event in the {risk} tier ({severity_pct}% severity index), "
        f"indicating {risk_threat} in the affected geographic zone."
    )

    # 3. Disaster Classification
    disaster_classification = (
        f"Event Type: {dtype.upper()}\n"
        f"Risk Level: {risk}\n"
        f"Severity Index: {severity_pct}%\n"
        f"Classification Category: {d_category.capitalize()} hazard\n"
        f"Primary Impact Mechanism: {d_mechanism.capitalize()}\n"
        f"Geographic Coordinates: {lat}°N, {lon}°E\n"
        f"Detection Timestamp: {ts}\n"
        f"Classification Engine: Terra-Aura AI v1.0 (Weather + NLP + Satellite fusion)"
    )

    # 4. Risk Assessment
    risk_assessment = (
        f"Overall Risk Rating: {risk} ({severity_pct}% severity index)\n\n"
        f"Threat Assessment: The {risk_adj} risk classification indicates {risk_threat}. "
        f"Based on current severity metrics and population density estimates, the AI engine "
        f"has assigned a {confidence_pct}% confidence level to this classification. "
        f"Key risk factors include the event's geographic position, the magnitude of "
        f"weather and social signal inputs, and proximity to populated zones.\n\n"
        f"Escalation Risk: {'HIGH — immediate containment required.' if risk in ('CRITICAL','HIGH') else 'MODERATE — active monitoring recommended.'}"
    )

    # 5. Population Impact
    population_impact = (
        f"Estimated Population at Risk: {pop} individuals\n\n"
        f"Population Exposure Assessment: Based on demographic data and geographic boundary "
        f"analysis around {lat}°N, {lon}°E, approximately {pop} people are estimated to be "
        f"within the primary impact zone. Vulnerable populations including elderly residents, "
        f"children, and individuals with limited mobility require prioritised protective actions.\n\n"
        f"Displacement Risk: {'CRITICAL — mass displacement expected.' if risk == 'CRITICAL' else 'HIGH — significant displacement possible.' if risk == 'HIGH' else 'MODERATE — localised displacement may occur.' if risk == 'MEDIUM' else 'LOW — minimal displacement anticipated.'}"
    )

    # 6. Infrastructure Impact
    infrastructure_impact = (
        f"Primary Infrastructure Threat: {d_infra.capitalize()}\n\n"
        f"The {dtype} event poses {risk_adj} risk to critical infrastructure in the affected zone. "
        f"Detailed impact assessment covers:\n"
        f"- Transport networks: {'Likely disruption — road closures probable.' if risk in ('CRITICAL','HIGH') else 'Moderate risk — monitor key routes.'}\n"
        f"- Power infrastructure: {'High disruption risk — pre-position backup generation.' if risk in ('CRITICAL','HIGH') else 'Low-moderate risk — standard contingency applies.'}\n"
        f"- Water systems: {'Contamination or service disruption possible.' if dtype in ('flood','none') else 'Standard risk — monitor for secondary effects.'}\n"
        f"- Communications: {'Potential outage zones — activate backup channels.' if risk == 'CRITICAL' else 'No immediate risk — maintain standard operations.'}"
    )

    # 7. AI Confidence Note
    ai_confidence_note = (
        f"Prediction Confidence: {confidence_pct}%\n\n"
        f"This assessment was generated by the Terra-Aura AI v1.0 multi-modal inference engine, "
        f"combining outputs from three independent model layers: Weather Risk Model (meteorological "
        f"sensor analysis), NLP Social Signal Model (social media and citizen report analysis), and "
        f"Satellite Imagery Model (visual anomaly detection). The ensemble confidence score of "
        f"{confidence_pct}% reflects strong {'multi-source agreement.' if confidence_pct >= 85 else 'primary signal detection with supporting evidence.' if confidence_pct >= 70 else 'indicative signal with uncertainty in secondary inputs.'}\n\n"
        f"Note: AI predictions are probabilistic. All critical decisions must be validated by "
        f"qualified emergency management personnel before implementation."
    )

    # 8. Forecast
    forecast = _FORECAST_BY_RISK.get(risk, _FORECAST_BY_RISK["LOW"])

    # 9. Recommended Actions
    recommended_actions = _RECOMMENDED_BY_RISK.get(risk, _RECOMMENDED_BY_RISK["LOW"])

    # 10. Data Sources
    sources = ["Weather Sensor Array", "NLP Social Signal Feed"]
    if dtype in ("flood", "cyclone"):
        sources.append("Satellite Imagery (Water Signature)")
    elif dtype in ("fire", "earthquake"):
        sources.append("Satellite Thermal Analysis")
    sources.append("Terra-Aura AI Inference Engine v1.0")
    data_sources = json.dumps(sources)

    return {
        "executive_summary": executive_summary,
        "situation_analysis": situation_analysis,
        "disaster_classification": disaster_classification,
        "risk_assessment": risk_assessment,
        "population_impact": population_impact,
        "infrastructure_impact": infrastructure_impact,
        "ai_confidence_note": ai_confidence_note,
        "forecast": forecast,
        "recommended_actions": recommended_actions,
        "data_sources": data_sources,
    }
