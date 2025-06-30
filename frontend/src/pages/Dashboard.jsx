// frontend/src/pages/Dashboard.jsx
import { useEffect, useState } from 'react';
import { useApi } from '../utils/api';

export default function Dashboard() {
  const api = useApi();

  const [adminData, setAdminData] = useState(null);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState('');

  useEffect(() => {
    (async () => {
      try {
        /* 1️⃣ Who am I? */
        const { user } = await api.get('/users/me');

        /* 2️⃣ Regular users just stop here */
        if (user.role !== 'admin') {
          setAdminData({ role: 'user' });
          return;
        }

        /* 3️⃣ Admin analytics – helper already returns parsed JSON */
        const [reservations, slots, activeUsers] = await Promise.all([
          api.get('/reports/reservations-per-day').then(r => r.data),
          api.get('/reports/slot-summary').then(r => r.data),
          api.get('/reports/active-users').then(r => r.data),
        ]);

        setAdminData({ role: 'admin', reservations, slots, activeUsers });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    })();
  }, [api]);

  /* ---------------- render ---------------- */
  if (loading) return <p className="p-4">Loading…</p>;
  if (error)   return <p className="p-4 text-red-600">{error}</p>;

  if (adminData.role !== 'admin') {
    return <p className="p-4">Hi there – no admin analytics for regular users.</p>;
  }

  return (
    <div className="p-6 space-y-10">
      <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>

      {/* Reservations */}
      <section>
        <h2 className="text-xl font-bold mb-2">Reservations (Last 7 Days)</h2>
        <ul className="bg-white shadow p-4">
          {adminData.reservations.map(d => (
            <li key={d.day}>{d.day}: {d.count}</li>
          ))}
        </ul>
      </section>

      {/* Slot summary */}
      <section>
        <h2 className="text-xl font-bold mb-2">Slot Availability</h2>
        <ul className="bg-white shadow p-4">
          {adminData.slots.map(l => (
            <li key={l.location_id}>
              {l.location_name}: {l.available}/{l.total}
            </li>
          ))}
        </ul>
      </section>

      {/* Active users */}
      <section>
        <h2 className="text-xl font-bold mb-2">Active Users</h2>
        <ul className="bg-white shadow p-4 space-y-2">
          {adminData.activeUsers.map(u => (
            <li key={u.user_id}>
              <strong>{u.first_name} {u.last_name}</strong> — {u.email}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
