// src/pages/Login.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function Login() {
  const navigate        = useNavigate();
  const { login }       = useAuth();
  const [mode, setMode] = useState('login');   // 'login' | 'register'

  const [form, setForm] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name : '',
  });

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  /* ---------- submit ---------- */
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      /* register (optional) */
      if (mode === 'register') {
        if (form.password !== form.confirmPassword)
          throw new Error('Passwords do not match');

        const res = await fetch('/api/auth/register', {
          method : 'POST',
          headers: { 'Content-Type': 'application/json' },
          body   : JSON.stringify({
            email      : form.email,
            password   : form.password,
            first_name : form.first_name,
            last_name  : form.last_name,
          }),
        });
        if (!res.ok) throw new Error((await res.json()).error || 'Registration failed');
      }

      /* login */
      const loginRes = await fetch('/api/auth/login', {
        method : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body   : JSON.stringify({ email: form.email, password: form.password }),
      });
      if (!loginRes.ok) throw new Error((await loginRes.json()).error || 'Login failed');

      const { access_token } = await loginRes.json();
      login(access_token);
      localStorage.setItem('token', access_token);
      toast.success('Welcome!');
      navigate('/');
    } catch (err) {
      toast.error(err.message);
    }
  };

  const swapMode = () => {
    setForm({
      email: '',
      password: '',
      confirmPassword: '',
      first_name: '',
      last_name : '',
    });
    setMode((m) => (m === 'login' ? 'register' : 'login'));
  };

  /* ---------- UI ---------- */
  return (
    <main className="min-h-screen flex items-center justify-center px-4 py-16 bg-gradient-to-br from-blue-700 via-indigo-700 to-purple-700">
      <div className="w-full max-w-md space-y-6 backdrop-blur-md bg-white/10 border border-white/20 rounded-3xl p-8 shadow-2xl">
        <h1 className="text-center text-3xl font-extrabold text-white drop-shadow">
          {mode === 'login' ? 'Sign in to Smart Parking' : 'Create your account'}
        </h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            name="email"
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={handleChange}
            className="w-full min-w-0 rounded-lg bg-white/90 py-2 px-3 focus:outline-none"
            required
          />

          {mode === 'register' && (
            <>
              {/* first / last row becomes vertical < sm */}
              <div className="flex flex-col sm:flex-row gap-2">
                <input
                  name="first_name"
                  placeholder="First name"
                  value={form.first_name}
                  onChange={handleChange}
                  className="w-full sm:flex-1 min-w-0 rounded-lg bg-white/90 py-2 px-3"
                  required
                />
                <input
                  name="last_name"
                  placeholder="Last name"
                  value={form.last_name}
                  onChange={handleChange}
                  className="w-full sm:flex-1 min-w-0 rounded-lg bg-white/90 py-2 px-3"
                  required
                />
              </div>
              <input
                name="confirmPassword"
                type="password"
                placeholder="Confirm password"
                value={form.confirmPassword}
                onChange={handleChange}
                className="w-full min-w-0 rounded-lg bg-white/90 py-2 px-3"
                required
              />
            </>
          )}

          <input
            name="password"
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={handleChange}
            className="w-full min-w-0 rounded-lg bg-white/90 py-2 px-3"
            required
          />

          <button
            type="submit"
            className="w-full py-2 rounded-lg bg-gradient-to-r from-yellow-400 via-orange-500 to-pink-500
                       text-white font-semibold tracking-wide hover:scale-[1.03] transition"
          >
            {mode === 'login' ? 'Login' : 'Register'}
          </button>
        </form>

        <p className="text-center text-sm text-white/80">
          {mode === 'login' ? (
            <>
              Need an account?{' '}
              <button onClick={swapMode} className="underline font-medium">
                Register
              </button>
            </>
          ) : (
            <>
              Already have an account?{' '}
              <button onClick={swapMode} className="underline font-medium">
                Sign in
              </button>
            </>
          )}
        </p>
      </div>
    </main>
  );
}
