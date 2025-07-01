// src/pages/Home.jsx
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Home() {
  const { user } = useAuth();
  const asUser = user?.role === 'admin' && localStorage.getItem('sp_asUser') === 'true';
  const isAdminView = user?.role === 'admin' && !asUser;

  /* ---------- card presets ---------- */
  const adminCards = [
    {
      icon: '🗺️',
      title: 'Interactive Map',
      blurb: 'Manage intuitively',
      to: '/admin/locations',
    },
    {
      icon: '🛡️',
      title: 'User Management',
      blurb: 'Roles & access control',
      to: '/admin/users',
    },
    {
      icon: '📊',
      title: 'Actionable Insights',
      blurb: 'Analytics & trends',
      to: '/dashboard',
    },
  ];

  const userCards = [
    {
      icon: '🗺️',
      title: 'Interactive Map',
      blurb: 'Find parking visually',
      to: '/locations',
    },
    {
      icon: '⚡',
      title: 'Fast Live Booking',
      blurb: 'Reserve in seconds',
      to: '/locations',
    },
    {
      icon: '❌',
      title: 'Easy Cancellations',
      blurb: 'Manage your bookings',
      to: '/my-reservations',
    },
  ];

  const cards = isAdminView ? adminCards : userCards;

  return (
    <main
      className="
        relative min-h-[calc(100vh-6rem)] flex flex-col items-center justify-center
        bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 text-white
        overflow-hidden
      "
    >
      {/* subtle grain texture */}
      <div
        className="
          pointer-events-none absolute inset-0 opacity-[0.06] mix-blend-overlay
          bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3Lncz
          Lm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjYwIiBoZWlnaHQ9IjYwIiBmaWxsPSIjZmZmIi8+
          PGNpcmNsZSBmaWxsPSIjZGRkIiByPSIxIiBjeD0iMTIiIGN5PSI2Ii8+PGNpcmNsZSBmaWxsPSIj
          ZGRkIiByPSIxIiBjeD0iMjQiIGN5PSIyMCIvPjxjaXJjbGUgZmlsbD0iI2RkZCIgcj0iMSIgY3g9
          IjQ1IiBjeT0iMzUiLz48L3N2Zz4=')]
        "
      />

      {/* decorative blobs */}
      <div className="absolute -top-48 -left-40 w-[32rem] h-[32rem] bg-indigo-400 rounded-full opacity-20 blur-[120px]" />
      <div className="absolute -bottom-48 -right-36 w-[38rem] h-[38rem] bg-pink-500 rounded-full opacity-20 blur-[120px]" />

      {/* hero / CTA */}
      <section className="relative z-10 text-center px-6">
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight drop-shadow-lg">
          Park with Ingenuity.
        </h1>
        <p className="mt-4 max-w-xl mx-auto text-lg sm:text-xl text-indigo-100">
          Real‑time slot availability, effortless reservations and admin analytics – all in one app.
        </p>

        <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
          {isAdminView ? (
            <>
              {/* force Admin Mode */}
              <Link
                to="/dashboard"
                onClick={() => localStorage.setItem('sp_asUser', 'false')}
                className="px-6 py-3 rounded-lg bg-white/90 text-blue-700 font-semibold shadow hover:bg-white transition"
              >
                Go to Dashboard
              </Link>

              {/* switch to User Mode and reload Home */}
              <Link
                to="/"
                onClick={(e) => {
                  e.preventDefault();
                  localStorage.setItem('sp_asUser', 'true');
                  window.location.href = '/';
                }}
                className="px-6 py-3 rounded-lg bg-white/10 backdrop-blur-md border border-white/30 hover:bg-white/20 transition"
              >
                View as User
              </Link>
            </>
          ) : (
            <Link
              to="/locations"
              className="px-8 py-3 rounded-lg bg-white text-blue-700 font-semibold shadow hover:scale-[1.03] transition"
            >
              Find Parking Now
            </Link>
          )}
        </div>
      </section>

      {/* feature cards */}
      <div className="relative z-10 mt-16 sm:mt-24 w-full max-w-6xl px-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {cards.map(({ icon, title, blurb, to }) => (
            <Link
              key={title}
              to={to}
              className="group backdrop-blur-md bg-white/10 border border-white/20 rounded-2xl p-6
                         text-left text-white shadow hover:shadow-lg transition
                         focus:outline-none focus:ring-2 focus:ring-white/40"
            >
              <div className="text-3xl group-hover:scale-110 transition">{icon}</div>
              <h3 className="mt-2 text-lg font-semibold">{title}</h3>
              <p className="mt-1 text-sm text-indigo-100">{blurb}</p>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
