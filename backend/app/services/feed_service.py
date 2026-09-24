import logging
from typing import List, Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

USGS_ALL_HOUR_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
USGS_ALL_DAY_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"


async def fetch_usgs_earthquakes(min_magnitude: float = 1.0) -> List[Dict[str, Any]]:
    """
    Asynchronously queries USGS GeoJSON feeds for real-time seismic events.
    Filters features by minimum magnitude threshold and transforms to standard platform schema.
    Applies a strict 5.0s timeout to protect backend responsiveness.
    """
    results: List[Dict[str, Any]] = []

    urls_to_try = [USGS_ALL_HOUR_URL]
    # If looking for higher magnitude or need more events, query all_day feed
    if min_magnitude >= 0.0:
        urls_to_try.append(USGS_ALL_DAY_URL)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            for url in urls_to_try:
                try:
                    response = await client.get(url)
                    if response.status_code != 200:
                        logger.warning(f"USGS feed query returned non-200 status: {response.status_code} ({url})")
                        continue

                    data = response.json()
                    features = data.get("features", [])

                    for feature in features:
                        props = feature.get("properties") or {}
                        geom = feature.get("geometry") or {}
                        coords = geom.get("coordinates") or []

                        mag = props.get("mag")
                        if mag is None:
                            continue

                        try:
                            mag_float = float(mag)
                        except (ValueError, TypeError):
                            continue

                        if mag_float < min_magnitude:
                            continue

                        if len(coords) < 2:
                            continue

                        lon = float(coords[0])
                        lat = float(coords[1])
                        depth_km = float(coords[2]) if len(coords) > 2 else 0.0
                        place = props.get("place") or "Unknown Location"
                        time_ms = props.get("time")

                        item = {
                            "external_id": feature.get("id"),
                            "title": f"M {mag_float:.1f} - {place}",
                            "disaster_type": "earthquake",
                            "latitude": lat,
                            "longitude": lon,
                            "raw_telemetry": {
                                "magnitude": mag_float,
                                "depth_km": depth_km,
                                "place": place,
                                "time": time_ms,
                                "seismic_magnitude": mag_float,
                            },
                            "source_origin": "USGS",
                        }
                        results.append(item)

                    # If all_hour had matches, no need to check all_day
                    if results:
                        break

                except httpx.TimeoutException:
                    logger.warning(f"Timeout querying USGS feed at {url}")
                except Exception as e:
                    logger.warning(f"Error querying USGS feed at {url}: {e}")

    except Exception as e:
        logger.error(f"Unexpected error in fetch_usgs_earthquakes: {e}")

    # Deduplicate within current fetched batch by external_id
    seen = set()
    deduped = []
    for item in results:
        eid = item.get("external_id")
        if eid and eid not in seen:
            seen.add(eid)
            deduped.append(item)
        elif not eid:
            deduped.append(item)

    return deduped


async def fetch_weather_telemetry(lat: float, lon: float) -> Dict[str, Any]:
    """
    Asynchronously queries Open-Meteo for real-time atmospheric readings at (lat, lon).
    Extracts precipitation rate (mm) and sustained 10m wind speed (km/h).
    Applies a strict 5.0s timeout with safe deterministic fallback.
    """
    url = (
        f"{OPEN_METEO_BASE_URL}?latitude={lat:.4f}&longitude={lon:.4f}"
        f"&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
    )

    fallback_data = {
        "precipitation": 0.0,
        "wind_speed_10m": 0.0,
        "temperature_2m": 20.0,
        "relative_humidity_2m": 50.0,
        "weather_rainfall": 0.0,
        "weather_wind_speed": 0.0,
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code != 200:
                logger.warning(f"Open-Meteo returned status {response.status_code} for ({lat}, {lon})")
                return fallback_data

            data = response.json()
            current = data.get("current") or {}

            precipitation = float(current.get("precipitation") or 0.0)
            wind_speed = float(current.get("wind_speed_10m") or 0.0)
            temp = float(current.get("temperature_2m") or 20.0)
            humidity = float(current.get("relative_humidity_2m") or 50.0)

            return {
                "precipitation": precipitation,
                "wind_speed_10m": wind_speed,
                "temperature_2m": temp,
                "relative_humidity_2m": humidity,
                "weather_rainfall": precipitation,
                "weather_wind_speed": wind_speed,
            }

    except httpx.TimeoutException:
        logger.warning(f"Open-Meteo request timed out for coordinates ({lat}, {lon})")
        return fallback_data
    except Exception as e:
        logger.warning(f"Error fetching Open-Meteo weather for ({lat}, {lon}): {e}")
        return fallback_data
