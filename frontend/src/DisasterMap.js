import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix Leaflet marker issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

function DisasterMap({ disasters = [], onSelectDisaster }) {
  const hasDisasters = disasters.length > 0;

  return (
    <MapContainer
      center={hasDisasters ? [disasters[0].latitude, disasters[0].longitude] : [20.5937, 78.9629]}
      zoom={5}
      className="disaster-map"
    >
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {disasters.map((d) => (
        <Marker
          key={d.id}
          position={[d.latitude, d.longitude]}
          eventHandlers={{
            click: () => onSelectDisaster?.(d),
          }}
        >
          <Popup>
            <b>Type:</b> {d.disaster_type} <br />
            <b>Risk:</b> {d.risk_level} <br />
            <b>Severity:</b> {d.severity_score}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}

export default DisasterMap;
