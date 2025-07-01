// src/pages/Locations.jsx
/*
  🗺️  Parking Locations Map (Davao City)
  --------------------------------------------------------------------
  • Click pin → flyTo + highlight list item (no redirect)
  • List click still flyTo + highlight, arrow still opens booking
  --------------------------------------------------------------------
*/

import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MapContainer, TileLayer, Marker, Tooltip, Popup, useMap,
} from 'react-leaflet';
import L from 'leaflet';
import { useApi } from '../utils/api';
import 'leaflet/dist/leaflet.css';

/* ——— fix Leaflet marker assets in Vite ——— */
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl      : new URL('leaflet/dist/images/marker-icon.png',   import.meta.url).href,
  shadowUrl    : new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
});

/* ——— fit map bounds once locations load ——— */
function FitBounds({ markers }) {
  const map = useMap();
  useEffect(() => {
    if (!markers.length) return;
    map.fitBounds(L.latLngBounds(markers.map((m) => [m.lat, m.lng])).pad(0.25));
  }, [markers, map]);
  return null;
}

export default function Locations() {
  const api      = useApi();
  const navigate = useNavigate();
  const mapRef   = useRef(null);

  const [locs, setLocs] = useState([]);
  const [sel,  setSel ] = useState(null);
  const [err,  setErr ] = useState('');
  const [load, setLoad] = useState(true);

  /* ——— fetch locations & sort ——— */
  useEffect(() => {
    (async () => {
      try {
        const { locations } = await api.get('/parking_location/locations');
        locations.sort((a, b) => a.name.localeCompare(b.name));
        setLocs(locations);
      } catch (e) {
        setErr(e.message);
      } finally {
        setLoad(false);
      }
    })();
  }, [api]);

  if (load) return <p className="p-4 text-white">Loading locations…</p>;
  if (err)  return <p className="p-4 text-red-300">{err}</p>;

  /* ——— focus / highlight helper ——— */
  const focusPin = (loc) => {
    mapRef.current?.flyTo([loc.lat, loc.lng], 17, { duration: 0.8 });
    setSel(loc.id);
  };

  const listItem = (loc) => {
    const active = loc.id === sel;
    return (
      <li
        key={loc.id}
        onClick={() => focusPin(loc)}
        className={`group flex items-center justify-between gap-4 p-4 cursor-pointer transition
                    ${active ? 'bg-white/25 shadow-inner ring-2 ring-yellow-400/70' : 'hover:bg-white/10'}`}
      >
        <div>
          <p className="font-semibold text-white">{loc.name}</p>
          <p className="text-sm text-gray-200">{loc.address}</p>
        </div>

        {active && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/locations/${loc.id}/slots`, { state: loc });
            }}
            className="shrink-0 p-2 rounded-lg bg-gradient-to-r from-yellow-400 via-orange-500 to-pink-500 text-white text-2xl leading-none shadow-lg hover:scale-[1.08] transition"
            title="Book slots"
          >
            ➜
          </button>
        )}
      </li>
    );
  };

  return (
    <main className="relative min-h-[calc(100vh-6rem)] flex flex-col gap-8 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 text-white overflow-hidden p-6">
      {/* grain overlay */}
      <div className="pointer-events-none absolute inset-0 opacity-[0.06] mix-blend-overlay bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjYwIiBoZWlnaHQ9IjYwIiBmaWxsPSIjZmZmIi8+PGNpcmNsZSBmaWxsPSIjZGRkIiByPSIxIiBjeD0iMTIiIGN5PSI2Ii8+PGNpcmNsZSBmaWxsPSIjZGRkIiByPSIxIiBjeD0iMjQiIGN5PSIyMCIvPjxjaXJjbGUgZmlsbD0iI2RkZCIgcj0iMSIgY3g9IjQ1IiBjeT0iMzUiLz48L3N2Zz4=')]" />

      <h1 className="relative z-10 text-4xl sm:text-5xl font-extrabold drop-shadow-lg">
        Parking Locations
      </h1>

      <div className="relative z-10 flex flex-col md:flex-row gap-6">
        {/* ——— map ——— */}
        <div className="flex-1 backdrop-blur-md bg-white/10 border border-white/20 rounded-3xl shadow-2xl overflow-hidden shrink-0">
          <MapContainer
            center={[7.19, 125.46]}
            zoom={13}
            scrollWheelZoom
            className="h-[70vh] w-full"
            ref={mapRef}
          >
            <TileLayer attribution="&copy; OpenStreetMap" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            <FitBounds markers={locs} />

            {locs.map((loc) => (
              <Marker
                key={loc.id}
                position={[loc.lat, loc.lng]}
                eventHandlers={{
                  click: () => focusPin(loc),              // ← changed behaviour
                }}
              >
                <Tooltip direction="top" offset={[0, -28]} opacity={0.9}>
                  <div className="text-xs leading-tight">
                    <strong>{loc.name}</strong><br />
                    {loc.address}<br />
                    Slots: {loc.available_slots}
                  </div>
                </Tooltip>

                {/* popup kept purely for “view slots” button */}
                <Popup>
                  <strong>{loc.name}</strong><br />
                  {loc.address}<br />
                  <button
                    onClick={() => navigate(`/locations/${loc.id}/slots`, { state: loc })}
                    className="mt-2 inline-block rounded-md px-2 py-1 text-xs font-semibold bg-gradient-to-r from-yellow-400 via-orange-500 to-pink-500 text-white shadow hover:scale-[1.05] transition"
                  >
                    View slots&nbsp;→
                  </button>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>

        {/* ——— list ——— */}
        <aside
          className="md:w-80 h-[70vh] overflow-y-auto
                     [scrollbar-width:none] [&::-webkit-scrollbar]:hidden
                     backdrop-blur-md bg-white/10 border border-white/20 rounded-3xl shadow-2xl shrink-0"
        >
          <h2 className="sticky top-0 z-10 px-4 py-3 font-semibold text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-700 rounded-t-3xl">
            All Locations
          </h2>

          <ul className="divide-y divide-white/20">
            {locs.map(listItem)}
          </ul>
        </aside>
      </div>
    </main>
  );
}
