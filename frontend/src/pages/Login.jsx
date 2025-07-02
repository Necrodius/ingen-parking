import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useApi } from '../utils/api';
import toast from 'react-hot-toast';

/* single source for clearing the form -------------------------- */
const EMPTY = {
  email: '', password: '', confirmPassword: '', first_name: '', last_name: '',
};

export default function Login() {
  const navigate  = useNavigate();
  const { login } = useAuth();
  const api       = useApi();

  /* ui mode: 'login' | 'register'  (JS version) */
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState(EMPTY);

  /* keep inputs in sync */
  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  /* submit handler */
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (mode === 'register') {
        if (form.password !== form.confirmPassword)
          throw new Error('Passwords do not match');

        await api.post('/auth/register', {
          email: form.email, password: form.password,
          first_name: form.first_name, last_name: form.last_name,
        });
        toast.success('Registration complete! Please sign in.');
        setMode('login');
        return;
      }

      const { access_token } = await api.post('/auth/login', {
        email: form.email, password: form.password,
      });

      login(access_token);
      localStorage.setItem('token', access_token);
      toast.success('Welcome!');
      navigate('/');
    } catch (err) {
      toast.error(err.message);
    }
  };

  /* switch form + clear fields */
  const swapMode = () => { setForm(EMPTY); setMode(mode === 'login' ? 'register' : 'login'); };

  return (
    <main className="
        min-h-screen flex items-center justify-center
        p-4 sm:p-8 md:p-12 lg:p-16
        bg-gradient-to-br from-blue-700 via-indigo-700 to-purple-700">
      <div className="
          w-full max-w-[90vw] sm:max-w-sm md:max-w-md lg:max-w-lg xl:max-w-xl
          space-y-6 sm:space-y-8
          backdrop-blur-md bg-white/10 border border-white/20
          rounded-3xl md:rounded-[2rem] p-5 sm:p-6 md:p-8 lg:p-10
          shadow-2xl">
        <h1 className="
            text-center font-extrabold drop-shadow text-3xl
            sm:text-4xl md:text-5xl text-white">
          {mode === 'login' ? 'Sign in to Smart Parking' : 'Create your account'}
        </h1>

        <form onSubmit={handleSubmit} className="space-y-4 md:space-y-6">
          {/* email */}
          <input
            name="email" type="email" placeholder="Email"
            value={form.email} onChange={handleChange}
            className="w-full rounded-lg bg-white/90 py-2.5 px-3 focus:outline-none" required />

          {/* register‑only fields */}
          {mode === 'register' ? (
            <>
              <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
                <input name="first_name" placeholder="First name" value={form.first_name}
                  onChange={handleChange} className="flex-1 rounded-lg bg-white/90 py-2.5 px-3" required />
                <input name="last_name" placeholder="Last name" value={form.last_name}
                  onChange={handleChange} className="flex-1 rounded-lg bg-white/90 py-2.5 px-3" required />
              </div>
              <input name="password" type="password" placeholder="Password"
                value={form.password} onChange={handleChange}
                className="w-full rounded-lg bg-white/90 py-2.5 px-3" required />
              <input name="confirmPassword" type="password" placeholder="Confirm password"
                value={form.confirmPassword} onChange={handleChange}
                className="w-full rounded-lg bg-white/90 py-2.5 px-3" required />
            </>
          ) : (
            /* login mode: just password */
            <input name="password" type="password" placeholder="Password"
              value={form.password} onChange={handleChange}
              className="w-full rounded-lg bg-white/90 py-2.5 px-3" required />
          )}

          <button type="submit" className="
              w-full rounded-lg font-semibold tracking-wide text-white
              py-2 sm:py-2.5 md:py-3
              bg-gradient-to-r from-yellow-400 via-orange-500 to-pink-500
              hover:scale-[1.03] transition">
            {mode === 'login' ? 'Login' : 'Register'}
          </button>
        </form>

        <p className="text-center text-sm sm:text-base text-white/80">
          {mode === 'login' ? (
            <>Need an account? <button onClick={swapMode} className="underline font-medium">Register</button></>
          ) : (
            <>Already have an account? <button onClick={swapMode} className="underline font-medium">Sign in</button></>
          )}
        </p>
      </div>
    </main>
  );
}
