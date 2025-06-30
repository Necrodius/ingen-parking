// src/pages/Login.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [mode, setMode] = useState('login'); // "login" | "register"

  const [form, setForm] = useState({
    email: '',
    password: '',
    confirmPassword: '',  // for register only
    first_name: '',
    last_name: '',
  });

  const [error, setError] = useState('');

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      if (mode === 'register') {
        // validate match
        if (form.password !== form.confirmPassword) {
          throw new Error('Passwords do not match');
        }

        // REGISTER
        const res = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: form.email,
            password: form.password,
            first_name: form.first_name,
            last_name: form.last_name,
          }),
        });

        if (!res.ok) {
          const { error } = await res.json();
          throw new Error(error || 'Registration failed');
        }
      }

      // LOGIN (after register or manually)
      const loginRes = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: form.email,
          password: form.password,
        }),
      });

      if (!loginRes.ok) {
        const { error } = await loginRes.json();
        throw new Error(error || 'Login failed');
      }

      const { access_token } = await loginRes.json();
      login(access_token);
      localStorage.setItem('token', access_token);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    }
  };

  const toggleMode = () => {
    setError('');
    setForm({
      email: '',
      password: '',
      confirmPassword: '',
      first_name: '',
      last_name: '',
    });
    setMode((prev) => (prev === 'login' ? 'register' : 'login'));
  };

  return (
    <section className="max-w-md mx-auto mt-16">
      <h1 className="text-2xl font-bold mb-4 text-center">
        {mode === 'login' ? 'Login' : 'Register'}
      </h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          name="email"
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          className="w-full border p-2"
          required
        />

        {mode === 'register' && (
          <>
            <input
              name="first_name"
              type="text"
              placeholder="First Name"
              value={form.first_name}
              onChange={handleChange}
              className="w-full border p-2"
              required
            />
            <input
              name="last_name"
              type="text"
              placeholder="Last Name"
              value={form.last_name}
              onChange={handleChange}
              className="w-full border p-2"
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
          className="w-full border p-2"
          required
        />

        {mode === 'register' && (
          <input
            name="confirmPassword"
            type="password"
            placeholder="Confirm Password"
            value={form.confirmPassword}
            onChange={handleChange}
            className="w-full border p-2"
            required
          />
        )}

        {error && <p className="text-red-600 text-sm">{error}</p>}

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded"
        >
          {mode === 'login' ? 'Sign In' : 'Create Account'}
        </button>
      </form>

      <p className="text-center mt-4 text-sm">
        {mode === 'login' ? (
          <>
            Need an account?{' '}
            <button className="text-blue-600 underline" onClick={toggleMode}>
              Register
            </button>
          </>
        ) : (
          <>
            Already have an account?{' '}
            <button className="text-blue-600 underline" onClick={toggleMode}>
              Login
            </button>
          </>
        )}
      </p>
    </section>
  );
}
