/*
  Profile.jsx
  ————————————————————————————————————————————
  • Loads user via GET /api/users/me (captures id)
  • Lets user edit first / last name
  • Allows password change
  • Uses profile.id for PUT /users/<id> routes
*/

import { useEffect, useState } from 'react';
import { useApi } from '../utils/api';
import toast from 'react-hot-toast';

export default function Profile() {
  const api = useApi();

  /* ───────── state ───────── */
  const [loading, setLoading] = useState(true);
  const [err,     setErr]     = useState('');

  const [profile, setProfile] = useState({
    id: null,
    first_name: '',
    last_name: '',
    email: '',
  });

  const [pw, setPw] = useState({
    old_password: '',
    new_password: '',
    confirm: '',
  });

  /* ───────── fetch on mount ───────── */
  useEffect(() => {
    (async () => {
      try {
        const { user: me } = await api.get('/users/me');
        setProfile({
          id:         me.id,          // ⬅️ capture id here
          first_name: me.first_name,
          last_name:  me.last_name,
          email:      me.email,
        });
      } catch (e) {
        setErr(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, [api]);

  /* ───────── save profile ───────── */
  const saveProfile = async () => {
    try {
      await api.put(`/users/${profile.id}`, {
        first_name: profile.first_name,
        last_name:  profile.last_name,
        // email: profile.email, // enable if editable
      });
      toast.success('Profile updated');
    } catch (e) {
      toast.error(e.message);
    }
  };

  /* ───────── change password ───────── */
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
      toast.success('Password changed');
      setPw({ old_password: '', new_password: '', confirm: '' });
    } catch (e) {
      toast.error(e.message);
    }
  };

  /* ───────── UI states ───────── */
  if (loading) return <p className="p-4">Loading profile…</p>;
  if (err)     return <p className="p-4 text-red-600">{err}</p>;

  return (
    <section className="max-w-lg mx-auto p-6 space-y-8">
      <h1 className="text-2xl font-bold">My Profile</h1>

      {/* Basic Info */}
      <div className="space-y-4 border p-4 rounded-lg">
        <h2 className="font-semibold">Basic Info</h2>
        <input
          className="w-full border p-2 rounded"
          placeholder="First Name"
          value={profile.first_name}
          onChange={(e) =>
            setProfile({ ...profile, first_name: e.target.value })
          }
        />
        <input
          className="w-full border p-2 rounded"
          placeholder="Last Name"
          value={profile.last_name}
          onChange={(e) =>
            setProfile({ ...profile, last_name: e.target.value })
          }
        />
        <input
          disabled
          className="w-full border p-2 rounded bg-gray-100"
          placeholder="Email"
          value={profile.email}
          onChange={(e) =>
            setProfile({ ...profile, email: e.target.value })
          }
        />
        <button
          onClick={saveProfile}
          className="bg-blue-600 text-white py-2 px-4 rounded"
        >
          Save
        </button>
      </div>

      {/* Change Password */}
      <div className="space-y-4 border p-4 rounded-lg">
        <h2 className="font-semibold">Change Password</h2>
        <input
          type="password"
          className="w-full border p-2 rounded"
          placeholder="Current Password"
          value={pw.old_password}
          onChange={(e) => setPw({ ...pw, old_password: e.target.value })}
        />
        <input
          type="password"
          className="w-full border p-2 rounded"
          placeholder="New Password"
          value={pw.new_password}
          onChange={(e) => setPw({ ...pw, new_password: e.target.value })}
        />
        <input
          type="password"
          className="w-full border p-2 rounded"
          placeholder="Confirm New Password"
          value={pw.confirm}
          onChange={(e) => setPw({ ...pw, confirm: e.target.value })}
        />
        <button
          onClick={changePw}
          className="bg-blue-600 text-white py-2 px-4 rounded"
        >
          Update Password
        </button>
      </div>
    </section>
  );
}
