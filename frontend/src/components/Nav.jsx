import { useEffect, useState, useRef } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useNotifications } from '../context/NotificationContext';

/*
  🛳  Responsive NavBar – v2.1
  • Better spacing
  • Tools ordered Slider → Bell → Profile
  • Profile arrow flips
  • Slider label restored (desktop & mobile)
*/
export default function Nav() {
  /* ── Auth / notifications / navigation ── */
  const { user, logout }      = useAuth();
  const { list, markAllRead } = useNotifications();
  const navigate              = useNavigate();

  /* 1️⃣  “View as user” toggle (admins only) */
  const [asUser, setAsUser] = useState(
    () => localStorage.getItem('sp_asUser') === 'true'
  );
  useEffect(() => localStorage.setItem('sp_asUser', asUser), [asUser]);

  const toggleMode = () => {
    const next = !asUser;
    localStorage.setItem('sp_asUser', next);
    setAsUser(next);
    window.location.href = '/';
  };

  /* 2️⃣  Logout */
  const handleLogout = () => {
    localStorage.removeItem('sp_asUser');
    logout();
    navigate('/login');
  };

  /* 3️⃣  Generic “click outside to close” hook */
  const useClickOutside = (ref, setter) => {
    useEffect(() => {
      const handler = (e) => {
        if (ref.current && !ref.current.contains(e.target)) setter(false);
      };
      document.addEventListener('mousedown', handler);
      return () => document.removeEventListener('mousedown', handler);
    }, [ref, setter]);
  };

  /* ─ Profile dropdown ─ */
  const [profileOpen, setProfileOpen] = useState(false);
  const profileRef = useRef(null);
  useClickOutside(profileRef, setProfileOpen);

  /* ─ Notification tray ─ */
  const [notifOpen, setNotifOpen] = useState(false);
  const notifRef = useRef(null);
  useClickOutside(notifRef, setNotifOpen);

  /* 4️⃣  Mobile menu state */
  const [mobileOpen, setMobileOpen] = useState(false);
  const closeMobile = () => setMobileOpen(false);

  /* 5️⃣  Helpers */
  const unread  = list.filter((n) => !n.read).length;
  const latest5 = list.slice(0, 5);

  /* – Shared link style – */
  const navClass = ({ isActive }) =>
    `px-3 py-1 rounded transition ${
      isActive ? 'bg-blue-600 text-white' : 'hover:bg-gray-700'
    }`;

  /* – Role‑based link blocks – */
  const userLinks = (
    <>
      <NavLink to="/locations"       onClick={closeMobile} className={navClass}>
        Locations
      </NavLink>
      <NavLink to="/my-reservations" onClick={closeMobile} className={navClass}>
        My Reservations
      </NavLink>
    </>
  );

  const adminLinks = (
    <>
      <NavLink to="/dashboard"       onClick={closeMobile} className={navClass}>
        Dashboard
      </NavLink>
      <NavLink to="/admin/locations" onClick={closeMobile} className={navClass}>
        Manage Locations
      </NavLink>
      <NavLink to="/admin/users"     onClick={closeMobile} className={navClass}>
        Manage Users
      </NavLink>
    </>
  );

  /* 6️⃣  Markup */
  return (
    <nav
      className="sticky top-2 mx-2 lg:mx-auto max-w-6xl z-50
                 bg-gray-800/95 backdrop-blur-md text-white
                 px-4 py-3 rounded-lg shadow-lg"
    >
      {/* ── Top row ── */}
      <div className="flex justify-between items-center">
        {/* Logo – extra right‑margin for breathing room */}
        <Link
          to="/"
          className="font-semibold text-lg hover:opacity-90 mr-6 md:mr-10"
          onClick={closeMobile}
        >
          Smart Parking
        </Link>

        {/* 🍔  (mobile only) */}
        <button
          className="md:hidden p-2 rounded hover:bg-gray-700 focus:outline-none"
          onClick={() => setMobileOpen((o) => !o)}
          aria-label="Toggle menu"
        >
          ☰
        </button>

        {/* Desktop links + tools */}
        <div className="hidden md:flex items-center gap-6">
          {/* Main links */}
          {user?.role === 'user' && userLinks}
          {user?.role === 'admin' && (asUser ? userLinks : adminLinks)}

          {/* Right‑side tool strip: Slider → Bell → Profile */}
          {user && (
            <>
              {/* 1. Admin/User slider with label */}
              {user.role === 'admin' && (
                <label
                  className="relative inline-flex items-center cursor-pointer select-none"
                  title="Toggle Admin/User mode"
                >
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={asUser}
                    onChange={toggleMode}
                  />
                  <div className="w-11 h-6 bg-gray-400 peer-checked:bg-blue-600 rounded-full transition-colors"></div>
                  <div className="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform peer-checked:translate-x-5 shadow"></div>
                  <span className="ml-3 text-sm">
                    {asUser ? 'User Mode' : 'Admin Mode'}
                  </span>
                </label>
              )}

              {/* 2. Notification bell */}
              <div className="relative" ref={notifRef}>
                <button
                  onClick={() => {
                    setNotifOpen((o) => !o);
                    if (!notifOpen) markAllRead();
                  }}
                  className="relative p-2 rounded-full hover:bg-gray-700"
                  title="Notifications"
                >
                  🔔
                  {unread > 0 && (
                    <span className="absolute -top-1 -right-1 text-xs bg-red-600 rounded-full px-1.5">
                      {unread}
                    </span>
                  )}
                </button>

                {notifOpen && (
                  <div className="absolute right-0 mt-2 w-64 bg-white text-gray-900 rounded shadow z-50">
                    <p className="px-4 py-2 font-semibold border-b">Notifications</p>
                    {latest5.length === 0 ? (
                      <p className="px-4 py-3 text-sm text-gray-500">No notifications.</p>
                    ) : (
                      <ul className="max-h-60 overflow-y-auto">
                        {latest5.map((n) => (
                          <li key={n.id} className="px-4 py-2 border-b text-sm">
                            {n.msg}
                            <br />
                            <span className="text-xs text-gray-500">
                              {n.ts.toLocaleString('en-PH', { timeZone: 'Asia/Manila' })}
                            </span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}
              </div>

              {/* 3. Profile dropdown (arrow flips) */}
              <div className="relative" ref={profileRef}>
                <button
                  onClick={() => setProfileOpen((o) => !o)}
                  className="flex items-center gap-1 px-3 py-1 rounded hover:bg-gray-700"
                >
                  👤
                  <span
                    className={`text-xs transition-transform ${
                      profileOpen ? 'rotate-180' : ''
                    }`}
                  >
                    ▾
                  </span>
                </button>

                {profileOpen && (
                  <div className="absolute right-0 mt-2 w-40 bg-white text-gray-900 rounded shadow z-50">
                    <NavLink
                      to="/profile"
                      onClick={() => {
                        setProfileOpen(false);
                        closeMobile();
                      }}
                      className="flex items-center gap-2 px-4 py-2 hover:bg-gray-100"
                    >
                      👤 Profile
                    </NavLink>
                    <button
                      onClick={handleLogout}
                      className="flex items-center gap-2 w-full text-left px-4 py-2 hover:bg-gray-100"
                    >
                      🚪 Logout
                    </button>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Mobile dropdown */}
      {mobileOpen && (
        <div className="md:hidden flex flex-col gap-3 mt-4 p-4 bg-gray-800 rounded-lg shadow-lg z-50">
          {user?.role === 'user' && userLinks}
          {user?.role === 'admin' && (asUser ? userLinks : adminLinks)}
          <hr className="border-gray-700" />

          {user && (
            <>
              {/* Slider (mobile) with label */}
              {user.role === 'admin' && (
                <label
                  className="relative inline-flex items-center cursor-pointer select-none mb-3"
                  title="Toggle Admin/User mode"
                >
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={asUser}
                    onChange={toggleMode}
                  />
                  <div className="w-11 h-6 bg-gray-400 peer-checked:bg-blue-600 rounded-full transition-colors"></div>
                  <div className="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform peer-checked:translate-x-5 shadow"></div>
                  <span className="ml-3 text-sm">
                    {asUser ? 'User Mode' : 'Admin Mode'}
                  </span>
                </label>
              )}

              {/* Bell (mobile) */}
              <button
                onClick={() => {
                  setNotifOpen((o) => !o);
                  if (!notifOpen) markAllRead();
                }}
                className="relative flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-700 mb-2"
              >
                🔔 Notifications
                {unread > 0 && (
                  <span className="text-xs bg-red-600 rounded-full px-1.5">
                    {unread}
                  </span>
                )}
              </button>

              {/* Profile & logout (mobile) */}
              <NavLink
                to="/profile"
                onClick={closeMobile}
                className="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-700"
              >
                👤 Profile
              </NavLink>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-700"
              >
                🚪 Logout
              </button>
            </>
          )}
        </div>
      )}
    </nav>
  );
}
