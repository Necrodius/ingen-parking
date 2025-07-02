import { useEffect, useRef, useState } from 'react';
import {
  MapContainer,
  TileLayer,
  Marker,
  Tooltip,
  useMap,
  useMapEvent,
} from 'react-leaflet';
import L from 'leaflet';
import toast from 'react-hot-toast';
import 'leaflet/dist/leaflet.css';

import { useApi } from '../utils/api';
import { useNotifications } from '../context/NotificationContext';

/* ───────── Fix Leaflet marker assets (Vite) ───────── */
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl:       new URL('leaflet/dist/images/marker-icon.png',   import.meta.url).href,
  shadowUrl:     new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
});

/* ───────── Utility: fit map bounds ───────── */
function FitBounds({ markers }) {
  const map = useMap();
  useEffect(() => {
    if (!markers.length) return;
    map.fitBounds(L.latLngBounds(markers.map((m) => [m.lat, m.lng])).pad(0.25));
  }, [markers, map]);
  return null;
}

/* ───────── Utility: capture map click while “Add” is active ───────── */
function AddLocationHandler({ addMode, onPick }) {
  useMapEvent('click', (e) => {
    if (!addMode) return;
    onPick(e.latlng);
  });
  return null;
}

/* ───────── Main page ───────── */
export default function AdminLocations() {
  const api           = useApi();
  const { notify }    = useNotifications();
  const mapRef        = useRef(null);
  const liRefs        = useRef({});       // 🔄 collect refs for auto‑scroll

  const [locs,  setLocs]  = useState([]);
  const [sel,   setSel]   = useState(null);
  const [load,  setLoad]  = useState(true);
  const [err,   setErr]   = useState('');
  const [modal, setModal] = useState(null);  // {mode,data}
  const [slots, setSlots] = useState(null);  // location obj
  const [addMode, setAdd] = useState(false);

  /* fetch & sort */
  const fetchLocations = () =>
    api.get('/parking_location/locations')
       .then((r) => {
         r.locations.sort((a, b) => a.name.localeCompare(b.name));
         setLocs(r.locations);
       })
       .catch((e) => setErr(e.message))
       .finally(() => setLoad(false));

  useEffect(() => { fetchLocations(); }, [api]);

  /* auto‑scroll list when selection changes */
  useEffect(() => {
    if (sel && liRefs.current[sel]) {
      liRefs.current[sel].scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [sel]);

  /* helpers */
  const focusPin = (loc) => {
    mapRef.current?.flyTo([loc.lat, loc.lng], 17, { duration: 0.8 });
    setSel(loc.id);
  };

  const saveLocation = (body, id) => {
    const payload = { ...body, lat: +body.lat, lng: +body.lng };
    const req     = id
      ? api.put(`/parking_location/locations/${id}`, payload)
      : api.post('/parking_location/locations',        payload);
    return req.then(fetchLocations);
  };

  const deleteLocation = (id) =>
    api.del(`/parking_location/locations/${id}`).then(fetchLocations);

  const handleAddPick = ({ lat, lng }) => {
    setAdd(false);
    setModal({ mode: 'create', data: { name: '', address: '', lat: lat.toFixed(6), lng: lng.toFixed(6) } });
  };

  /* loading / error states */
  if (load) return <p className="p-4 text-white">Loading locations…</p>;
  if (err)  return <p className="p-4 text-red-300">{err}</p>;

  /* list item */
  const listItem = (loc) => {
    const active = loc.id === sel;
    return (
      <li
        key={loc.id}
        ref={(el) => (liRefs.current[loc.id] = el)}
        onClick={() => focusPin(loc)}
        className={`group flex items-center justify-between gap-4 p-4 cursor-pointer transition
                    ${active ? 'bg-white/25 ring-2 ring-yellow-400/70 shadow-inner' : 'hover:bg-white/10'}
                    odd:bg-white/[0.03]`}
      >
        <div>
          <p className="font-semibold text-white">{loc.name}</p>
          <p className="text-sm text-indigo-100">{loc.address}</p>
        </div>

        {active && (
          <div className="flex gap-2">
            <button
              onClick={(e) => { e.stopPropagation(); setSlots(loc); }}
              className="p-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700"
              title="Manage slots"
            >🗂️</button>
            <button
              onClick={(e) => { e.stopPropagation(); setModal({ mode: 'edit', data: loc }); }}
              className="p-1.5 rounded-lg bg-blue-600 hover:bg-blue-700"
              title="Edit location"
            >✏️</button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                if (!window.confirm('Delete this location?')) return;
                deleteLocation(loc.id)
                  .then(() => notify('Location deleted'))
                  .catch((err) => toast.error(err.message));
              }}
              className="p-1.5 rounded-lg bg-red-600 hover:bg-red-700"
              title="Delete location"
            >🗑️</button>
          </div>
        )}
      </li>
    );
  };

  /* render */
  return (
    <main className="relative min-h-[calc(100vh-6rem)] flex flex-col gap-8 bg-gradient-to-br from-blue-700 via-indigo-800 to-purple-800 text-white overflow-hidden p-6">
      {/* noise overlay */}
      <div className="pointer-events-none absolute inset-0 opacity-[0.05] mix-blend-overlay bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjYwIiBoZWlnaHQ9IjYwIiBmaWxsPSIjZmZmIi8+PGNpcmNsZSBmaWxsPSIjZGRkIiByPSIxIiBjeD0iMTIiIGN5PSI2Ii8+PGNpcmNsZSBmaWxsPSIjZGRkIiByPSIxIiBjeD0iMjQiIGN5PSIyMCIvPjxjaXJjbGUgZmlsbD0iI2RkZCIgcj0iMSIgY3g9IjQ1IiBjeT0iMzUiLz48L3N2Zz4=')" />

      <h1 className="relative z-10 text-4xl sm:text-5xl font-extrabold drop-shadow-md">
        Manage Parking Locations
      </h1>

      <div className="relative z-10 flex flex-col md:flex-row gap-6">
        {/* Map card */}
        <div className={`flex-1 backdrop-blur-md bg-white/10 border border-white/20 rounded-3xl shadow-2xl overflow-hidden shrink-0 ${addMode && 'cursor-crosshair'}`}>
          <MapContainer
            center={[7.19, 125.46]}
            zoom={13}
            scrollWheelZoom
            className="h-[70vh] w-full"
            ref={mapRef}
          >
            <TileLayer
              attribution="&copy; OpenStreetMap"
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <FitBounds markers={locs} />
            <AddLocationHandler addMode={addMode} onPick={handleAddPick} />

            {locs.map((loc) => (
              <Marker
                key={loc.id}
                position={[loc.lat, loc.lng]}
                eventHandlers={{ click: () => focusPin(loc) }}
              >
                <Tooltip direction="top" offset={[0, -28]} opacity={0.9}>
                  <div className="text-xs leading-tight">
                    <strong>{loc.name}</strong><br />
                    {loc.address}<br />
                    Slots: {loc.available_slots}
                  </div>
                </Tooltip>
              </Marker>
            ))}
          </MapContainer>
        </div>

        {/* Scrollable list */}
        <aside className="md:w-80 h-[70vh] overflow-y-auto pr-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden backdrop-blur-md bg-white/10 border border-white/20 rounded-3xl shadow-2xl shrink-0">
          {/* header */}
          <div className="sticky top-0 z-10 px-4 py-3 flex justify-between items-center bg-gradient-to-r from-blue-700 via-indigo-800 to-purple-800 rounded-t-3xl">
            <h2 className="font-semibold">All Locations</h2>
            <button
              onClick={() => { setSel(null); setAdd(true); toast('Click the map to place the new location'); }}
              className="p-1.5 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-600 hover:brightness-110"
              title="Add new location (click map after)"
            >➕</button>
          </div>

          <ul className="divide-y divide-white/10">{locs.map(listItem)}</ul>

          {locs.length === 0 && (
            <p className="text-center py-4 text-indigo-100">No locations yet.</p>
          )}
        </aside>
      </div>

      {/* Modals */}
      {modal && (
        <LocationModal
          initial={modal.data}
          onClose={() => setModal(null)}
          onSave={saveLocation}
          notify={notify}
        />
      )}
      {slots && (
        <SlotManagerModal
          location={slots}
          onClose={() => setSlots(null)}
          notify={notify}
        />
      )}
    </main>
  );
}

/* ───────── LocationModal (create / edit) ───────── */
function LocationModal({ initial, onClose, onSave, notify }) {
  const [form, setForm] = useState({
    name:    initial.name    || '',
    address: initial.address || '',
    lat:     initial.lat     || '',
    lng:     initial.lng     || '',
  });
  const [saving, setSaving] = useState(false);
  const isEdit = Boolean(initial.id);

  const handleSave = () => {
    if (!form.name.trim())                 return toast.error('Name is required');
    if (form.lat === '' || form.lng === '') return toast.error('Lat/Lng required');
    setSaving(true);
    onSave(form, initial.id)
      .then(() => { notify(isEdit ? 'Location updated' : 'Location created'); onClose(); })
      .catch((e) => toast.error(e.message))
      .finally(() => setSaving(false));
  };

  const input = (label, key, type = 'text') => (
    <label className="block text-sm font-medium">
      {label}
      <input
        type={type}
        value={form[key]}
        onChange={(e) => setForm({ ...form, [key]: e.target.value })}
        disabled={saving}
        className="mt-1 w-full rounded bg-slate-700 border border-slate-500 p-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-400"
      />
    </label>
  );

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
      <div className="w-96 rounded-2xl bg-slate-800 p-6 shadow-2xl space-y-4 text-white">
        <h3 className="text-lg font-semibold">{isEdit ? 'Edit Location' : 'New Location'}</h3>
        {input('Name', 'name')}
        {input('Address', 'address')}
        {input('Latitude', 'lat', 'number')}
        {input('Longitude', 'lng', 'number')}

        <div className="flex justify-end gap-2 pt-2">
          <button onClick={onClose} disabled={saving} className="rounded px-3 py-1 border border-slate-500 hover:bg-slate-700 disabled:opacity-60">Cancel</button>
          <button onClick={handleSave} disabled={saving} className="rounded px-3 py-1 bg-gradient-to-r from-emerald-500 to-teal-600 hover:brightness-110 disabled:opacity-60">
            {saving ? 'Saving…' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ───────── SlotManagerModal ───────── */
function SlotManagerModal({ location, onClose, notify }) {
  const api                   = useApi();
  const [slots, setSlots]     = useState([]);
  const [label, setLabel]     = useState('');
  const [loading, setLoading] = useState(true);

  const loadSlots = () =>
    api.get(`/parking_slot/slots?location_id=${location.id}`)
       .then((r) => setSlots(r.slots))
       .catch((e) => toast.error(e.message))
       .finally(() => setLoading(false));

  useEffect(() => { loadSlots(); }, [api, location.id]);

  const addSlot = () => {
    const trimmed = label.trim();
    if (!trimmed) return;
    api.post('/parking_slot/slots', { location_id: location.id, slot_label: trimmed })
       .then(() => { notify('Slot added'); setLabel(''); loadSlots(); })
       .catch((e) => toast.error(e.message));
  };

  const deleteSlot = (id) =>
    api.del(`/parking_slot/slots/${id}`)
       .then(() => { notify('Slot deleted'); loadSlots(); })
       .catch((e) => toast.error(e.message));

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
      <div className="w-[28rem] max-h-[90vh] overflow-y-auto rounded-2xl bg-slate-800 p-6 shadow-2xl space-y-4 text-white">
        <h3 className="text-lg font-semibold">Slots for “{location.name}”</h3>

        <div className="flex gap-2">
          <input
            type="text"
            placeholder="New slot label"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            className="flex-1 rounded bg-slate-700 border border-slate-500 p-2 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-400"
          />
          <button onClick={addSlot} className="rounded px-3 py-1 bg-gradient-to-r from-emerald-500 to-teal-600 hover:brightness-110">Add</button>
        </div>

        {loading ? (
          <p>Loading…</p>
        ) : (
          <ul className="space-y-1">
            {slots.map((s) => (
              <li key={s.id} className="flex justify-between items-center rounded bg-slate-700 p-2">
                <span>{s.slot_label}</span>
                <button
                  onClick={() => window.confirm('Delete this slot?') && deleteSlot(s.id)}
                  className="p-1.5 rounded bg-red-600 hover:bg-red-700"
                >🗑️</button>
              </li>
            ))}
            {slots.length === 0 && <li className="text-center py-2 text-indigo-100">No slots yet.</li>}
          </ul>
        )}

        <div className="flex justify-end pt-2">
          <button onClick={onClose} className="rounded px-3 py-1 border border-slate-500 hover:bg-slate-700">Close</button>
        </div>
      </div>
    </div>
  );
}
