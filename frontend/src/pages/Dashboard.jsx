import { useEffect, useState } from 'react';
import { useApi } from '../utils/api';
import toast from 'react-hot-toast';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';

export default function Dashboard() {
  const api = useApi();

  /* ---------- state hooks ---------- */
  const [adminData, setAdminData] = useState(null);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState('');
  const [range,     setRange]     = useState(7);
  const [edit,      setEdit]      = useState(null);
  const [page,      setPage]      = useState(0);

  /* ---------- derived data (safe defaults) ---------- */
  const nowIso = new Date().toISOString();
  const reservations = adminData?.reservations ?? [];

  const activeAll = reservations
    .filter(r => {
      const st = r.status.split('.').pop();
      return ['booked', 'ongoing'].includes(st) && r.end_ts > nowIso;
    })
    .sort((a, b) => new Date(a.start_ts) - new Date(b.start_ts));

  const pageSize   = 5;
  const pageCount  = Math.ceil(activeAll.length / pageSize);
  const active     = activeAll.slice(page * pageSize, page * pageSize + pageSize);

  /* ---------- effects ---------- */
  useEffect(() => {
    const loadDashboard = async (days) => {
      setLoading(true);
      try {
        const { user } = await api.get('/users/me');
        if (user.role !== 'admin') { setAdminData({ role: 'user' }); return; }

        const [
          chart, slotSummary, reservations,
          slots, locations, users,
        ] = await Promise.all([
          api.get(`/reports/reservations-per-day?days=${days}`).then(r => r.data),
          api.get('/reports/slot-summary').then(r => r.data),
          api.get('/reservation/reservations').then(r => r.reservations),
          api.get('/parking_slot/slots').then(r => r.slots),
          api.get('/parking_location/locations').then(r => r.locations),
          api.get('/users/').then(r => r.users),
        ]);

        const slotMap     = Object.fromEntries(slots.map(s => [s.id, s]));
        const locationMap = Object.fromEntries(locations.map(l => [l.id, l]));
        const userMap     = Object.fromEntries(users.map(u => [u.id, `${u.first_name} ${u.last_name}`]));

        setAdminData({
          role: 'admin',
          chart,
          slotSummary,
          reservations,
          slotMap,
          locationMap,
          userMap,
        });
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    loadDashboard(range);
  }, [range, api]);

  /* reset page when list size changes */
  useEffect(() => { setPage(0); }, [activeAll.length]);

  /* ---------- helpers ---------- */
  const refreshList = () =>
    api.get('/reservation/reservations')
       .then(r => setAdminData(prev => prev ? { ...prev, reservations: r.reservations } : prev))
       .catch(e => toast.error(e.message));

  const flash = (p, msg) => p.then(() => { toast.success(msg); refreshList(); })
                             .catch(e  => toast.error(e.message));

  const cancel =  id => flash(api.post(`/reservation/reservations/${id}/cancel`), 'Cancelled');
  const finish =  id => flash(api.post(`/reservation/reservations/${id}/finish`), 'Finished');
  const remove =  id => flash(api.del (`/reservation/reservations/${id}`)      , 'Deleted');

  const saveEdit = () => {
    const { id, slot_id, start_ts, end_ts } = edit;
    flash(api.put(`/reservation/reservations/${id}`, { slot_id, start_ts, end_ts }), 'Updated')
      .then(() => setEdit(null));
  };

  const statusChip = (st) => {
    const cls = {
      booked   : 'bg-yellow-100 text-yellow-800',
      ongoing  : 'bg-green-100  text-green-800',
      completed: 'bg-gray-100  text-gray-800',
      cancelled: 'bg-red-100   text-red-800',
    }[st] || 'bg-gray-100 text-gray-800';
    return <span className={`px-2 py-0.5 rounded text-xs font-medium ${cls}`}>{st}</span>;
  };

  /* ---------- guards ---------- */
  if (loading) return <p className="p-4">Loading…</p>;
  if (error)   return <p className="p-4 text-red-600">{error}</p>;
  if (adminData?.role !== 'admin')
    return <p className="p-4">Hi there – no admin analytics for regular users.</p>;

  /* ---------- render ---------- */
  return (
    <div className="p-6 space-y-10">
      <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>

      {/* ——— reservations chart ——— */}
      <section>
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-xl font-bold">Reservations (Last {range} Days)</h2>
          <select value={range}
                  onChange={e => setRange(+e.target.value)}
                  className="border rounded px-2 py-1 text-sm">
            {[7, 14, 30, 90].map(d => (
              <option key={d} value={d}>Last {d} days</option>
            ))}
          </select>
        </div>
        <div className="bg-white shadow p-4 rounded-lg">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={adminData.chart}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day"
                     tickFormatter={d =>
                       new Date(d).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}/>
              <YAxis allowDecimals={false}/>
              <Tooltip labelFormatter={d => new Date(d).toLocaleDateString()}/>
              <Line type="monotone" dataKey="count" stroke="#2563eb" strokeWidth={2} dot={{ r: 3 }}/>
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* ——— slot summary ——— */}
      <section>
        <h2 className="text-xl font-bold mb-2">Slot Availability</h2>
        <ul className="bg-white shadow p-4 rounded-lg">
          {adminData.slotSummary.map(l => (
            <li key={l.location_id}>
              {l.location_name}: {l.available}/{l.total}
            </li>
          ))}
        </ul>
      </section>

      {/* ——— active reservations ——— */}
      <section>
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-xl font-bold">Active Reservations</h2>
          <button onClick={refreshList}
                  className="p-2 border rounded hover:bg-gray-100"
                  title="Refresh list">
            🔄
          </button>
        </div>

        <div className="overflow-x-auto bg-white shadow rounded-lg">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-100">
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
                const st      = r.status.split('.').pop();
                const slot    = adminData.slotMap[r.slot_id] || {};
                const loc     = adminData.locationMap[slot.location_id] || {};
                const slotLbl = `${loc.name || '—'} • ${slot.slot_label || r.slot_id}`;
                const userLbl = adminData.userMap[r.user_id] || r.user_id;

                return (
                  <tr key={r.id} className="border-t">
                    <td className="px-3 py-2">{slotLbl}</td>
                    <td className="px-3 py-2">{userLbl}</td>
                    <td className="px-3 py-2">{new Date(r.start_ts).toLocaleString()}</td>
                    <td className="px-3 py-2">{new Date(r.end_ts).toLocaleString()}</td>
                    <td className="px-3 py-2">{statusChip(st)}</td>
                    <td className="px-3 py-2 flex gap-2">
                      {st === 'booked' && (
                        <button onClick={() => cancel(r.id)}
                                className="p-1.5 rounded bg-yellow-500 hover:bg-yellow-600"
                                title="Cancel">
                          ❌
                        </button>
                      )}
                      {st === 'ongoing' && (
                        <button onClick={() => finish(r.id)}
                                className="p-1.5 rounded bg-green-600 hover:bg-green-700"
                                title="Finish">
                          ✔️
                        </button>
                      )}
                      <button onClick={() => setEdit({ ...r })}
                              className="p-1.5 rounded bg-blue-600 hover:bg-blue-700"
                              title="Edit">
                        ✏️
                      </button>
                      <button onClick={() => remove(r.id)}
                              className="p-1.5 rounded bg-red-600 hover:bg-red-700"
                              title="Delete">
                        🗑️
                      </button>
                    </td>
                  </tr>
                );
              })}
              {active.length === 0 && (
                <tr>
                  <td colSpan="6" className="text-center py-4 text-gray-500">
                    No active reservations.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* pagination */}
        {pageCount > 1 && (
          <div className="flex justify-center items-center gap-4 mt-2">
            <button
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
              className="p-1 border rounded disabled:opacity-30"
              title="Previous page"
            >
              ◀
            </button>
            <span className="text-sm">
              Page {page + 1} / {pageCount}
            </span>
            <button
              onClick={() => setPage(p => Math.min(pageCount - 1, p + 1))}
              disabled={page === pageCount - 1}
              className="p-1 border rounded disabled:opacity-30"
              title="Next page"
            >
              ▶
            </button>
          </div>
        )}
      </section>

      {/* ——— edit modal ——— */}
      {edit && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow w-80 space-y-4">
            <h3 className="font-semibold text-lg">
              Edit Reservation #{edit.id}
            </h3>

            <label className="block text-sm">Slot ID
              <input type="number"
                     value={edit.slot_id}
                     onChange={e => setEdit({ ...edit, slot_id: +e.target.value })}
                     className="border w-full p-1 rounded mt-1" />
            </label>

            <label className="block text-sm">Start Time
              <input type="datetime-local"
                     value={edit.start_ts.slice(0, 16)}
                     onChange={e => setEdit({ ...edit, start_ts: e.target.value })}
                     className="border w-full p-1 rounded mt-1" />
            </label>

            <label className="block text-sm">End Time
              <input type="datetime-local"
                     value={edit.end_ts.slice(0, 16)}
                     onChange={e => setEdit({ ...edit, end_ts: e.target.value })}
                     className="border w-full p-1 rounded mt-1" />
            </label>

            <div className="flex justify-end gap-2 pt-1">
              <button onClick={() => setEdit(null)}
                      className="px-3 py-1 border rounded hover:bg-gray-100">
                Cancel
              </button>
              <button onClick={saveEdit}
                      className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
