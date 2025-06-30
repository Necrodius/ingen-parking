import { useEffect, useState } from 'react';
import { useApi } from '../utils/api';

export default function Dashboard() {
  const api = useApi();

  const [adminData, setAdminData]       = useState(null);   // null = unknown yet
  const [loading,    setLoading]        = useState(true);
  const [error,      setError]          = useState('');

  useEffect(() => {
    (async () => {
      setLoading(true);
      setError('');

      try {
        /* -------- 1. who am I? -------- */
        const meRes = await api.get('/users/me');
        if (!meRes.ok) throw new Error('auth‑check failed (token?)');
        const { user } = await meRes.json();

        /* regular users do not need extra calls */
        if (user.role !== 'admin') {
          setAdminData({ role: 'user' });
          return;
        }

        /* -------- 2. admin analytics -------- */
        const [r1, r2, r3] = await Promise.all([
          api.get('/reports/reservations-per-day').then(r => r.json()),
          api.get('/reports/slot-summary').then(r => r.json()),
          api.get('/reports/active-users').then(r => r.json()),
        ]);

        setAdminData({
          role: 'admin',
          reservations: r1.data,
          slots:        r2.data,
          activeUsers:  r3.data,
        });
      } catch (err) {
        console.error(err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    })();
  }, [api]);

  if (loading)      return <p className="p-4">Loading…</p>;
  if (error)        return <p className="p-4 text-red-600">{error}</p>;
  if (!adminData)   return null;                     // should not happen

  /* ---------------- UI ---------------- */
  if (adminData.role !== 'admin') {
    return <p className="p-4">Hi there – no admin data for regular users.</p>;
  }

  return (
    <div className="p-6 space-y-10">
      <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>

      {/* reservations graph */}
      <section>
        <h2 className="text-xl font-bold mb-2">Reservations (Last 7 Days)</h2>
        <ul className="bg-white shadow p-4">
          {adminData.reservations.map(d => (
            <li key={d.day}>{d.day}: {d.count}</li>
          ))}
        </ul>
      </section>

      {/* slot summary */}
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

      {/* active users */}
      <section>
        <h2 className="text-xl font-bold mb-2">Active Users</h2>
        <ul className="bg-white shadow p-4 space-y-2">
          {adminData.activeUsers.map(u => (
            <li key={u.user_id}>
              <strong>{u.first_name} {u.last_name}</strong> — {u.email}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
