// src/pages/Dashboard.jsx
import { useEffect, useState, useMemo } from 'react';
import { useApi } from '../utils/api';
import toast from 'react-hot-toast';
import { useNotifications } from '../context/NotificationContext';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { localInputToIso, isoToLocalInput } from '../utils/datetime';

export default function Dashboard() {
  const api        = useApi();
  const { notify } = useNotifications();

  /* ───────── State ───────── */
  const [adminData, setAdminData] = useState(null);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState('');
  const [range,     setRange]     = useState(7);
  const [edit,      setEdit]      = useState(null);

  /* slot‑availability filter (defaults: now → +24 h) */
  const [from, setFrom] = useState(() => isoToLocalInput(new Date().toISOString()));
  const [to,   setTo]   = useState(() => isoToLocalInput(new Date(Date.now() + 86_400_000).toISOString()));

  /* ───────── Helpers ───────── */
  const refreshList = () =>
    api.get('/reservation/reservations')
       .then(({ reservations }) => setAdminData(p => (p ? { ...p, reservations } : p)))
       .catch(e => toast.error(e.message));

  const flash = (promise, msg) =>
    promise.then(() => { notify(msg); refreshList(); })
           .catch(e => toast.error(e.message));

  const cancel = id => flash(api.post(`/reservation/reservations/${id}/cancel`),  'Cancelled');
  const finish = id => flash(api.post(`/reservation/reservations/${id}/finish`),   'Finished');
  const remove = id => flash(api.del(`/reservation/reservations/${id}`),           'Deleted');

  const saveEdit = () => {
    const { id, slot_id, start_ts, end_ts } = edit;
    flash(api.put(`/reservation/reservations/${id}`, {
      slot_id,
      start_ts: localInputToIso(start_ts),
      end_ts:   localInputToIso(end_ts),
    }), 'Updated').then(() => setEdit(null));
  };

  /* ───────── Load data on mount / range change ───────── */
  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const { user } = await api.get('/users/me');
        if (user.role !== 'admin') { setAdminData({ role: 'user' }); return; }

        const [
          chart, reservations, slots, locations, users,
        ] = await Promise.all([
          api.get(`/reports/reservations-per-day?days=${range}`).then(r => r.data),
          api.get('/reservation/reservations').then(r            => r.reservations),
          api.get('/parking_slot/slots').then(r                  => r.slots),
          api.get('/parking_location/locations').then(r          => r.locations),
          api.get('/users/').then(r                              => r.users),
        ]);

        const slotMap     = Object.fromEntries(slots.map(s     => [s.id, s]));
        const locationMap = Object.fromEntries(locations.map(l => [l.id, l]));
        const userMap     = Object.fromEntries(users.map(u     => [u.id, `${u.first_name} ${u.last_name}`]));

        setAdminData({ role: 'admin', chart, reservations, slotMap, locationMap, userMap });
      } catch (e) { setError(e.message); } finally { setLoading(false); }
    })();
  }, [range, api]);

  /* ───────── Derived data ───────── */
  const nowIso = new Date().toISOString();
  const reservations = adminData?.reservations ?? [];

  const active = reservations
    .filter(r =>
      (r.status === 'ReservationStatus.booked' ||
       r.status === 'ReservationStatus.ongoing') &&
      r.end_ts > nowIso)
    .sort((a, b) => new Date(a.start_ts) - new Date(b.start_ts));

  const totalSlots = adminData ? Object.keys(adminData.slotMap).length : 0;

  /* unique slot‑ids that are booked/ongoing right now */
  const blockedSlotsCount = reservations.reduce((set, r) => {
    if (
      r.status === 'ReservationStatus.booked' ||
      r.status === 'ReservationStatus.ongoing'
    ) { set.add(r.slot_id); }
    return set;
  }, new Set()).size;

  /* availability per location within custom window */
  const availability = useMemo(() => {
    if (!adminData) return [];
    const { slotMap, locationMap } = adminData;

    const startIso = localInputToIso(from);
    const endIso   = localInputToIso(to);

    const totalByLoc   = {};
    const blockedSlots = {};

    /* total slots per location */
    Object.values(slotMap).forEach(s => {
      totalByLoc[s.location_id] = (totalByLoc[s.location_id] || 0) + 1;
    });

    /* mark blocked slots for the chosen window */
    reservations.forEach(r => {
      if (
        r.status !== 'ReservationStatus.booked' &&
        r.status !== 'ReservationStatus.ongoing'
      ) return;                                   // ignore cancelled / finished

      if (r.end_ts <= startIso || r.start_ts >= endIso) return; // outside window

      const slot = slotMap[r.slot_id];
      if (!slot) return;
      (blockedSlots[slot.location_id] ||= new Set()).add(slot.id);
    });

    /* final list */
    return Object.entries(locationMap).map(([id, loc]) => {
      const total   = totalByLoc[id]   || 0;
      const blocked = blockedSlots[id] ? blockedSlots[id].size : 0;
      return { id, name: loc.name, bookable: total - blocked, blocked, total };
    }).sort((a, b) => a.name.localeCompare(b.name));
  }, [adminData, from, to, reservations]);

  /* ───────── Guards ───────── */
  if (loading) return <p className="p-4 text-white">Loading…</p>;
  if (error)   return <p className="p-4 text-red-300">{error}</p>;
  if (adminData?.role !== 'admin')
    return <p className="p-4 text-white">Hi there – no admin analytics for regular users.</p>;

  /* misc helpers */
  const statusChip = st => {
    const cls = {
      booked   : 'bg-yellow-400 text-yellow-900',
      ongoing  : 'bg-green-400  text-green-900',
      finished : 'bg-gray-400   text-gray-900',
      cancelled: 'bg-red-400    text-red-900',
    }[st] || 'bg-gray-400 text-gray-900';
    return <span className={`px-2 py-0.5 rounded text-xs font-semibold ${cls}`}>{st}</span>;
  };

  /* ───────── UI ───────── */
  return (
    <main className="relative min-h-[calc(100vh-6rem)] flex flex-col gap-8 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 text-white overflow-hidden p-6">
      {/* grain overlay */}
      <div className="pointer-events-none absolute inset-0 opacity-[0.06] mix-blend-overlay bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjYwIiBoZWlnaHQ9IjYwIiBmaWxsPSIjZmZmIi8+PC9zdmc+')" />

      <h1 className="relative z-10 text-4xl font-extrabold drop-shadow-lg">Admin Dashboard</h1>

      <section className="relative z-10 space-y-10">

        {/* ───── KPI cards ───── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: 'Total Slots',         value: totalSlots },
            { label: 'Blocked Slots',       value: blockedSlotsCount },
            { label: 'Active Reservations', value: active.length },
            { label: `Last ${range} Days`,  value: adminData.chart.reduce((s, c) => s + c.count, 0) },
          ].map(({ label, value }) => (
            <div key={label}
                 className="backdrop-blur-md bg-white/10 border border-white/20 rounded-2xl p-4 shadow-2xl text-center">
              <p className="text-2xl font-bold">{value}</p>
              <p className="text-sm text-white/70">{label}</p>
            </div>
          ))}
        </div>

        {/* ───── Row (chart | slot availability) ───── */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          {/* Reservations chart */}
          <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-3xl shadow-2xl p-6">
            <div className="flex flex-wrap sm:flex-nowrap sm:items-end sm:justify-between gap-4 mb-4">
              <h2 className="text-xl font-bold flex-1">Reservations (Last {range} Days)</h2>
              <select
                value={range}
                onChange={e => setRange(+e.target.value)}
                className="bg-white text-gray-800 border px-2 py-1 rounded"
              >
                {[7, 14, 30, 90].map(d => <option key={d}>{d}</option>)}
              </select>
            </div>

            <ResponsiveContainer width="100%" aspect={1.6}>
              <LineChart data={adminData.chart}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" tick={{ fill: 'white' }} />
                <YAxis allowDecimals={false} tick={{ fill: 'white' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', color: 'white' }}
                  labelFormatter={d => new Date(d)
                    .toLocaleString('en-PH', { timeZone: 'Asia/Manila' })}
                />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#facc15"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Slot availability */}
          <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-3xl shadow-2xl p-6">
            <div className="flex flex-wrap lg:flex-nowrap gap-4 mb-4">
              <h2 className="flex-1 text-xl font-bold">Slot Availability</h2>

              <div className="grid grid-cols-2 gap-2 text-xs w-full sm:w-auto">
                <label className="flex flex-col">
                  From
                  <input
                    type="datetime-local"
                    value={from}
                    onChange={e => setFrom(e.target.value)}
                    className="mt-1 rounded bg-white/10 text-white p-1 border border-white/30"
                  />
                </label>
                <label className="flex flex-col">
                  To
                  <input
                    type="datetime-local"
                    value={to}
                    onChange={e => setTo(e.target.value)}
                    className="mt-1 rounded bg-white/10 text-white p-1 border border-white/30"
                  />
                </label>
              </div>
            </div>

            {availability.length ? (
              <ul className="space-y-4 max-h-[40vh] overflow-y-auto pr-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
                {availability.map(({ id, name, bookable, blocked, total }) => {
                  const pct   = total ? (bookable / total) * 100 : 0;
                  const color = bookable ? 'bg-green-500' : 'bg-red-500';

                  return (
                    <li key={id} className="bg-white/10 p-4 rounded-xl shadow-inner backdrop-blur-sm">
                      <div className="flex justify-between items-center mb-2">
                        <h3 className="font-medium">{name}</h3>
                        <span className="text-sm text-white/70">{bookable}/{total} bookable</span>
                      </div>
                      <div className="w-full h-2 bg-white/20 rounded">
                        <div className={`h-2 rounded ${color}`} style={{ width: `${pct}%` }} />
                      </div>
                      {!!blocked && (
                        <p className="mt-1 text-xs text-red-300">{blocked} blocked</p>
                      )}
                    </li>
                  );
                })}
              </ul>
            ) : (
              <p className="text-center text-white/70">No slots found.</p>
            )}
          </div>
        </div>

        {/* ───── Active reservations list ───── */}
        <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-3xl shadow-2xl p-6">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-xl font-bold">Active Reservations</h2>
            <button
              onClick={refreshList}
              className="p-2 rounded bg-white/20 hover:bg-white/30"
              title="Refresh list"
            >
              🔄
            </button>
          </div>

          {/* Desktop table */}
          <div className="hidden md:block max-h-[45vh] overflow-y-auto pr-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
            <table className="min-w-full text-sm text-white/90">
              <thead className="bg-white/10 sticky top-0">
                <tr>
                  <th className="px-3 py-2 text-left">Slot</th>
                  <th className="px-3 py-2 text-left">User</th>
                  <th className="px-3 py-2">Start</th>
                  <th className="px-3 py-2">End</th>
                  <th className="px-3 py-2">Status</th>
                  <th className="px-3 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {active.map(r => {
                  const st   = r.status.split('.').pop();           // "booked" | "ongoing"
                  const slot = adminData.slotMap[r.slot_id] || {};
                  const loc  = adminData.locationMap[slot.location_id] || {};

                  return (
                    <tr key={r.id} className="border-t border-white/20">
                      <td className="px-3 py-2">{`${loc.name || '—'} • ${slot.slot_label || r.slot_id}`}</td>
                      <td className="px-3 py-2">{adminData.userMap[r.user_id] || r.user_id}</td>
                      <td className="px-3 py-2">{new Date(r.start_ts)
                        .toLocaleString('en-PH')}</td>
                      <td className="px-3 py-2">{new Date(r.end_ts)
                        .toLocaleString('en-PH')}</td>
                      <td className="px-3 py-2">{statusChip(st)}</td>
                      <td className="px-3 py-2 flex gap-2">
                        {st === 'booked'  && (
                          <button
                            onClick={() => cancel(r.id)}
                            className="p-1.5 bg-yellow-500 hover:bg-yellow-600 rounded"
                          >❌</button>
                        )}
                        {st === 'ongoing' && (
                          <button
                            onClick={() => finish(r.id)}
                            className="p-1.5 bg-green-600 hover:bg-green-700 rounded"
                          >✔️</button>
                        )}
                        <button
                          onClick={() => setEdit({ ...r })}
                          className="p-1.5 bg-blue-600 hover:bg-blue-700 rounded"
                        >✏️</button>
                        <button
                          onClick={() => remove(r.id)}
                          className="p-1.5 bg-red-600 hover:bg-red-700 rounded"
                        >🗑️</button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Mobile list */}
          <ul className="md:hidden space-y-3 max-h-[45vh] overflow-y-auto pr-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
            {active.map(r => {
              const st   = r.status.split('.').pop();
              const slot = adminData.slotMap[r.slot_id] || {};
              const loc  = adminData.locationMap[slot.location_id] || {};

              return (
                <li key={r.id} className="border border-white/20 rounded-lg p-3 bg-white/5">
                  <details>
                    <summary className="cursor-pointer flex justify-between items-center">
                      <span>{`${loc.name || '—'} • ${slot.slot_label || r.slot_id}`}</span>
                      {statusChip(st)}
                    </summary>
                    <div className="mt-2 space-y-1 text-sm text-white/80">
                      <p>User: {adminData.userMap[r.user_id] || r.user_id}</p>
                      <p>Start: {new Date(r.start_ts)
                        .toLocaleString('en-PH')}</p>
                      <p>End:&nbsp; {new Date(r.end_ts)
                        .toLocaleString('en-PH')}</p>
                      <div className="flex gap-2 pt-1">
                        {st === 'booked' && (
                          <button
                            onClick={() => cancel(r.id)}
                            className="p-1 bg-yellow-500 hover:bg-yellow-600 rounded text-xs"
                          >❌</button>
                        )}
                        {st === 'ongoing' && (
                          <button
                            onClick={() => finish(r.id)}
                            className="p-1 bg-green-600 hover:bg-green-700 rounded text-xs"
                          >✔️</button>
                        )}
                        <button
                          onClick={() => setEdit({ ...r })}
                          className="p-1 bg-blue-600 hover:bg-blue-700 rounded text-xs"
                        >✏️</button>
                        <button
                          onClick={() => remove(r.id)}
                          className="p-1 bg-red-600 hover:bg-red-700 rounded text-xs"
                        >🗑️</button>
                      </div>
                    </div>
                  </details>
                </li>
              );
            })}
          </ul>
        </div>
      </section>

      {/* ───── Edit modal ───── */}
      {edit && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="backdrop-blur-md bg-white/10 text-white border border-white/20 p-6 rounded-xl w-96 space-y-4 shadow-2xl">
            <h3 className="font-semibold text-lg">Edit Reservation #{edit.id}</h3>

            <label className="block text-sm">
              Slot ID
              <input
                type="number"
                value={edit.slot_id}
                onChange={e => setEdit({ ...edit, slot_id: +e.target.value })}
                className="w-full p-2 mt-1 rounded bg-white/10 text-white border border-white/30"
              />
            </label>
            <label className="block text-sm">
              Start Time
              <input
                type="datetime-local"
                value={isoToLocalInput(edit.start_ts)}
                onChange={e => setEdit({ ...edit, start_ts: e.target.value })}
                className="w-full p-2 mt-1 rounded bg-white/10 text-white border border-white/30"
              />
            </label>
            <label className="block text-sm">
              End Time
              <input
                type="datetime-local"
                value={isoToLocalInput(edit.end_ts)}
                onChange={e => setEdit({ ...edit, end_ts: e.target.value })}
                className="w-full p-2 mt-1 rounded bg-white/10 text-white border border-white/30"
              />
            </label>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setEdit(null)}
                className="px-4 py-1 rounded hover:bg-white/20"
              >
                Cancel
              </button>
              <button
                onClick={saveEdit}
                className="px-4 py-1 bg-blue-600 rounded hover:bg-blue-700"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
