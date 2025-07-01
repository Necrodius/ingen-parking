// src/pages/AdminUsers.jsx
/*
  🛡️  Admin Users – themed, responsive, collapsible
  ———————————————————————————————————————————————————
  • Matches dashboard glass / gradient aesthetic
  • Table on ≥ md; accordion list on mobile
  • Grain overlay, invisible scrollbars
  • New‑admin & detail modals styled to match app
*/

import { useEffect, useState } from 'react';
import { useApi } from '../utils/api';
import toast from 'react-hot-toast';
import { useNotifications } from '../context/NotificationContext';

export default function AdminUsers() {
  const api          = useApi();
  const { notify }   = useNotifications();

  const [users,   setUsers]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState('');
  const [detail,  setDetail]  = useState(null);  // user obj
  const [create,  setCreate]  = useState(false); // show modal

  const loadUsers = () =>
    api.get('/users/')
       .then(r => setUsers(r.users))
       .catch(e => setError(e.message))
       .finally(() => setLoading(false));

  useEffect(() => { loadUsers(); }, [api]);

  /* helpers */
  const toggleActive = (u) =>
    api.put(`/users/${u.id}`, { active: !u.active })
       .then(() => { notify(`${u.email} ${u.active ? 'deactivated' : 'activated'}`); loadUsers(); })
       .catch(e   => toast.error(e.message));

  const promote = (u) =>
    api.put(`/users/${u.id}`, { role: 'admin' })
       .then(() => { notify(`${u.email} promoted to admin`); loadUsers(); })
       .catch(e   => toast.error(e.message));

  /* UI states */
  if (loading) return <p className="p-4 text-white">Loading…</p>;
  if (error)   return <p className="p-4 text-red-300">{error}</p>;

  /* common style */
  const noBar = { scrollbarWidth: 'none', msOverflowStyle: 'none' };

  return (
    <main className="relative min-h-[calc(100vh-6rem)] flex flex-col gap-8
                     bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700
                     text-white overflow-hidden p-6">

      {/* grain */}
      <div className="pointer-events-none absolute inset-0 opacity-[0.06] mix-blend-overlay
                      bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjYwIiBoZWlnaHQ9IjYwIiBmaWxsPSIjZmZmIi8+PC9zdmc+')]" />

      <section className="relative z-10 space-y-8 max-w-6xl w-full mx-auto">

        {/* header */}
        <div className="flex justify-between items-center">
          <h1 className="text-4xl font-extrabold drop-shadow">User Management</h1>
          <button
            onClick={() => setCreate(true)}
            className="flex items-center gap-1 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 shadow-lg transition">
            ➕ <span className="hidden sm:inline">New Admin</span>
          </button>
        </div>

        {/* glass card */}
        <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-3xl shadow-2xl p-6">

          {/* desktop table */}
          <div className="hidden md:block max-h-[60vh] overflow-y-auto pr-1" style={noBar}>
            <table className="min-w-full text-sm text-white/90">
              <thead className="sticky top-0 bg-white/10">
                <tr>
                  <th className="px-3 py-2 text-left">Email</th>
                  <th className="px-3 py-2 text-left">Name</th>
                  <th className="px-3 py-2 text-center">Role</th>
                  <th className="px-3 py-2 text-center">Active</th>
                  <th className="px-3 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id} className="border-t border-white/20">
                    <td className="px-3 py-2">{u.email}</td>
                    <td className="px-3 py-2">{u.first_name} {u.last_name}</td>
                    <td className="px-3 py-2 text-center">{u.role}</td>
                    <td className="px-3 py-2 text-center">{u.active ? '✅' : '🚫'}</td>
                    <td className="px-3 py-2 flex gap-2 justify-center">
                      <button onClick={() => setDetail(u)}       className="p-1.5 rounded bg-indigo-600 hover:bg-indigo-700" title="Details">🔍</button>
                      <button onClick={() => toggleActive(u)}    className="p-1.5 rounded bg-yellow-500 hover:bg-yellow-600" title={u.active ? 'Deactivate':'Activate'}>
                        {u.active ? '🚫' : '✅'}
                      </button>
                      {u.role === 'user' && (
                        <button
                          onClick={() => window.confirm('Promote to admin?') && promote(u)}
                          className="p-1.5 rounded bg-blue-600 hover:bg-blue-700" title="Promote to admin">⬆️
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
                {users.length === 0 && (
                  <tr><td colSpan={5} className="py-4 text-center text-white/70">No users found.</td></tr>
                )}
              </tbody>
            </table>
          </div>

          {/* mobile accordion */}
          <ul className="md:hidden space-y-3 max-h-[60vh] overflow-y-auto pr-1" style={noBar}>
            {users.map(u => (
              <li key={u.id} className="border border-white/20 rounded-lg p-3 bg-white/5">
                <details>
                  <summary className="cursor-pointer flex justify-between items-center">
                    <span>{u.email}</span>
                    <span>{u.active ? '✅' : '🚫'}</span>
                  </summary>

                  <div className="mt-2 space-y-1 text-sm text-white/80">
                    <p>Name: {u.first_name} {u.last_name}</p>
                    <p>Role: {u.role}</p>

                    <div className="flex gap-2 pt-1">
                      <button onClick={() => setDetail(u)}    className="p-1 bg-indigo-600 hover:bg-indigo-700 rounded text-xs" title="Details">🔍</button>
                      <button onClick={() => toggleActive(u)} className="p-1 bg-yellow-500 hover:bg-yellow-600 rounded text-xs"
                              title={u.active ? 'Deactivate':'Activate'}>{u.active?'🚫':'✅'}</button>
                      {u.role === 'user' && (
                        <button onClick={() => window.confirm('Promote to admin?') && promote(u)}
                                className="p-1 bg-blue-600 hover:bg-blue-700 rounded text-xs" title="Promote">⬆️</button>
                      )}
                    </div>
                  </div>
                </details>
              </li>
            ))}
            {users.length === 0 && (
              <li className="text-center py-4 text-white/70">No users found.</li>
            )}
          </ul>
        </div>
      </section>

      {/* modals */}
      {detail && <UserDetailModal user={detail} onClose={() => setDetail(null)} />}
      {create && <CreateAdminModal onClose={() => setCreate(false)} onSaved={loadUsers} />}
    </main>
  );
}

/* ───────── UserDetailModal ───────── */
function UserDetailModal({ user, onClose }) {
  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="backdrop-blur-md bg-white/10 text-white border border-white/20 rounded-2xl p-6 shadow-2xl w-96 space-y-2">
        <h3 className="text-lg font-semibold">User Details</h3>
        <p><strong>ID:</strong> {user.id}</p>
        <p><strong>Email:</strong> {user.email}</p>
        <p><strong>Name:</strong> {user.first_name} {user.last_name}</p>
        <p><strong>Role:</strong> {user.role}</p>
        <p><strong>Active:</strong> {user.active ? 'Yes' : 'No'}</p>
        <p><strong>Created:</strong> {new Date(user.created_at).toLocaleString('en-PH', { timeZone: 'Asia/Manila' })}</p>

        <div className="flex justify-end pt-2">
          <button onClick={onClose} className="px-4 py-1 rounded hover:bg-white/20">Close</button>
        </div>
      </div>
    </div>
  );
}

/* ───────── CreateAdminModal ───────── */
function CreateAdminModal({ onClose, onSaved }) {
  const api = useApi();
  const { notify } = useNotifications();
  const [form, setForm] = useState({ email:'', password:'', first_name:'', last_name:'' });
  const [saving, setSaving] = useState(false);

  const handleSave = () => {
    if (!form.email || !form.password) return toast.error('Email and password are required');
    setSaving(true);
    api.post('/users/', { ...form, role: 'admin' })
       .then(() => { notify('Admin account created'); onSaved(); onClose(); })
       .catch(e => toast.error(e.message))
       .finally(() => setSaving(false));
  };

  const input = (label, key, type='text') => (
    <label className="block text-sm">
      {label}
      <input
        type={type}
        value={form[key]}
        onChange={e => setForm({ ...form, [key]: e.target.value })}
        className="w-full mt-1 p-2 rounded bg-white/10 border border-white/30 placeholder-white/50"
        disabled={saving}
      />
    </label>
  );

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="backdrop-blur-md bg-white/10 text-white border border-white/20 rounded-2xl p-6 shadow-2xl w-96 space-y-4">
        <h3 className="text-lg font-semibold">New Admin</h3>

        {input('Email',      'email')}
        {input('Password',   'password',   'password')}
        {input('First Name', 'first_name')}
        {input('Last Name',  'last_name')}

        <div className="flex justify-end gap-2 pt-1">
          <button onClick={onClose} className="px-4 py-1 rounded hover:bg-white/20" disabled={saving}>Cancel</button>
          <button onClick={handleSave}
                  className="px-4 py-1 bg-blue-600 hover:bg-blue-700 rounded disabled:opacity-50"
                  disabled={saving}>
            {saving ? 'Saving…' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
}
