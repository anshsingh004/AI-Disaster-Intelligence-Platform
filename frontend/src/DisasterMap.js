import React, { useMemo } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./DisasterMap.css";
import L from "leaflet";

// Fallback for default Leaflet marker assets if needed
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

/**
 * Creates color-coded, tactical Leaflet divIcons reflecting incident threat levels.
 * CRITICAL markers display a live radar pulse animation.
 */
const createThreatIcon = (riskLevel) => {
  const level = (riskLevel || "MEDIUM").toUpperCase();
  const levelClass = `marker-${level.toLowerCase()}`;
  const isPulsing = level === "CRITICAL" ? "pulse-critical" : "";

  return L.divIcon({
    className: "custom-disaster-marker",
    html: `
      <div class="tactical-marker-pin ${levelClass} ${isPulsing}">
        <span class="marker-dot"></span>
      </div>
    `,
    iconSize: [26, 26],
    iconAnchor: [13, 13],
    popupAnchor: [0, -14],
  });
};

function DisasterMap({ disasters = [], onSelectDisaster, onOpenDossier }) {
  const hasDisasters = disasters.length > 0;
  const centerCoords = useMemo(() => {
    if (hasDisasters) {
      return [disasters[0].latitude, disasters[0].longitude];
    }
    return [20.5937, 78.9629];
  }, [hasDisasters, disasters]);

  return (
    <MapContainer
      center={centerCoords}
      zoom={hasDisasters ? 4 : 5}
      className="disaster-map"
      scrollWheelZoom={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {disasters.map((d) => {
        const icon = createThreatIcon(d.risk_level);
        const title = d.title || `${d.disaster_type?.toUpperCase()} Incident #${d.id}`;
        const summary = d.sitrep_summary || `Sensor telemetry indicates ${d.risk_level || 'active'} risk condition.`;
        const badgeClass = `badge badge-${(d.risk_level || 'medium').toLowerCase()}`;

        return (
          <Marker
            key={d.id}
            position={[d.latitude, d.longitude]}
            icon={icon}
            eventHandlers={{
              click: () => onSelectDisaster?.(d),
            }}
          >
            <Popup className="tactical-popup">
              <div className="popup-dossier-card">
                <div className="popup-dossier-header">
                  <span style={{ fontSize: "11px", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.5px", color: "var(--primary)" }}>
                    {d.disaster_type || "Hazard"}
                  </span>
                  <span className={badgeClass}>
                    {d.risk_level}
                  </span>
                </div>
                <h4 className="popup-dossier-title">{title}</h4>
                <p className="popup-dossier-summary">{summary}</p>
                <button
                  type="button"
                  className="popup-dossier-btn"
                  onClick={() => {
                    if (onOpenDossier) {
                      onOpenDossier(d);
                    } else if (onSelectDisaster) {
                      onSelectDisaster(d);
                    }
                  }}
                >
                  <span className="material-symbols-outlined" style={{ fontSize: 16 }}>assignment</span>
                  Open Tactical Dossier
                </button>
              </div>
            </Popup>
          </Marker>
        );
      })}
    </MapContainer>
  );
}

export default DisasterMap;
