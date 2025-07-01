// src/pages/Profile.jsx
/*
  🧑‍💼 Profile Page – Themed and Responsive
  ————————————————————————————————————————————
  • Loads user info via GET /users/me
  • Allows editing name and password change
  • Styled to match dashboard (blur, glass, contrast)
*/

import { useEffect, useState } from 'react';
import { useApi } from '../utils/api';
import toast from 'react-hot-toast';
import { useNotifications } from '../context/NotificationContext';

export default function Profile() {
  const api = useApi();
  const { notify } = useNotifications();

  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState('');
  const [profile, setProfile] = useState({
    id: null, first_name: '', last_name: '', email: '',
  });
  const [pw, setPw] = useState({
    old_password: '', new_password: '', confirm: '',
  });

  useEffect(() => {
    (async () => {
      try {
        const { user: me } = await api.get('/users/me');
        setProfile({
          id: me.id,
          first_name: me.first_name,
          last_name : me.last_name,
          email     : me.email,
        });
      } catch (e) {
        setErr(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, [api]);

  const saveProfile = async () => {
    try {
      await api.put(`/users/${profile.id}`, {
        first_name: profile.first_name,
        last_name : profile.last_name,
      });
      notify('Profile updated');
    } catch (e) {
      toast.error(e.message);
    }
  };

  const changePw = async () => {
    if (pw.new_password !== pw.confirm) {
      toast.error('Passwords do not match');
      return;
    }
    try {
      await api.post(`/users/${profile.id}/change-password`, {
        old_password: pw.old_password,
        new_password: pw.new_password,
      });
      notify('Password changed');
      setPw({ old_password: '', new_password: '', confirm: '' });
    } catch (e) {
      toast.error(e.message);
    }
  };

  if (loading) return <p className="p-4 text-white">Loading profile…</p>;
  if (err) return <p className="p-4 text-red-300">{err}</p>;

  return (
    <main className="relative min-h-[calc(100vh-6rem)] flex flex-col gap-8
                     bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700
                     text-white overflow-hidden p-6">

      {/* grain overlay */}
      <div className="pointer-events-none absolute inset-0 opacity-[0.06] mix-blend-overlay
                      bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjYwIiBoZWlnaHQ9IjYwIiBmaWxsPSIjZmZmIi8+PC9zdmc+')]" />

      <section className="relative z-10 max-w-xl w-full mx-auto space-y-10">

        <h1 className="text-4xl font-extrabold drop-shadow text-center">My Profile</h1>

        {/* Basic Info */}
        <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-2xl p-6 shadow-xl space-y-4">
          <h2 className="text-xl font-semibold mb-2">Basic Info</h2>

          <input
            className="w-full p-2 rounded bg-white/10 border border-white/30 placeholder-white/50"
            placeholder="First Name"
            value={profile.first_name}
            onChange={e => setProfile({ ...profile, first_name: e.target.value })}
          />
          <input
            className="w-full p-2 rounded bg-white/10 border border-white/30 placeholder-white/50"
            placeholder="Last Name"
            value={profile.last_name}
            onChange={e => setProfile({ ...profile, last_name: e.target.value })}
          />
          <input
            disabled
            className="w-full p-2 rounded bg-white/5 border border-white/30 text-white/60 cursor-not-allowed"
            placeholder="Email"
            value={profile.email}
          />

          <button
            onClick={saveProfile}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded shadow-lg transition">
            Save Changes
          </button>
        </div>

        {/* Change Password */}
        <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-2xl p-6 shadow-xl space-y-4">
          <h2 className="text-xl font-semibold mb-2">Change Password</h2>

          <input
            type="password"
            className="w-full p-2 rounded bg-white/10 border border-white/30 placeholder-white/50"
            placeholder="Current Password"
            value={pw.old_password}
            onChange={e => setPw({ ...pw, old_password: e.target.value })}
          />
          <input
            type="password"
            className="w-full p-2 rounded bg-white/10 border border-white/30 placeholder-white/50"
            placeholder="New Password"
            value={pw.new_password}
            onChange={e => setPw({ ...pw, new_password: e.target.value })}
          />
          <input
            type="password"
            className="w-full p-2 rounded bg-white/10 border border-white/30 placeholder-white/50"
            placeholder="Confirm New Password"
            value={pw.confirm}
            onChange={e => setPw({ ...pw, confirm: e.target.value })}
          />

          <button
            onClick={changePw}
            className="w-full bg-yellow-500 hover:bg-yellow-600 text-gray-900 font-semibold py-2 px-4 rounded shadow-lg transition">
            Update Password
          </button>
        </div>
      </section>
    </main>
  );
}
