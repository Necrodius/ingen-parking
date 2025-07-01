import { useEffect, useState, useRef } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useNotifications } from '../context/NotificationContext';

/**
 * Navigation bar component
 * 
 * Provides:
 * - Responsive navigation menu for both desktop and mobile.
 * - Role-based links for users and admins.
 * - Admin toggle to "view as user".
 * - Notification dropdown with unread count.
 * - Profile menu with logout and profile view.
 */
export default function Nav() {
  // Access authentication state and logout function
  const { user, logout } = useAuth();

  // Access notifications list and function to mark them as read
  const { list, markAllRead } = useNotifications();

  const navigate = useNavigate();

  /** 
   * Admin-only: Toggle between Admin and "View as User" mode
   * State is persisted in localStorage across page reloads
   */
  const [asUser, setAsUser] = useState(() => localStorage.getItem('sp_asUser') === 'true');

  useEffect(() => {
    localStorage.setItem('sp_asUser', asUser);
  }, [asUser]);

  const toggleMode = () => {
    const next = !asUser;
    localStorage.setItem('sp_asUser', next);
    setAsUser(next);
    window.location.href = '/'; // Reload to reflect mode change
  };

  /** 
   * Logout handler: clears state and navigates to login page
   */
  const handleLogout = () => {
    localStorage.removeItem('sp_asUser');
    logout();
    navigate('/login');
  };

  /**
   * Hook: Closes a dropdown when clicking outside its ref
   * Used for notifications and profile menus
   */
  const useClickOutside = (ref, setter) => {
    useEffect(() => {
      const handler = (e) => {
        if (ref.current && !ref.current.contains(e.target)) {
          setter(false);
        }
      };
      document.addEventListener('mousedown', handler);
      return () => document.removeEventListener('mousedown', handler);
    }, [ref, setter]);
  };

  // Profile dropdown state and ref
  const [profileOpen, setProfileOpen] = useState(false);
  const profileRef = useRef(null);
  useClickOutside(profileRef, setProfileOpen);

  // Notification dropdown state and ref
  const [notifOpen, setNotifOpen] = useState(false);
  const notifRef = useRef(null);
  useClickOutside(notifRef, setNotifOpen);

  // Mobile menu toggle
  const [mobileOpen, setMobileOpen] = useState(false);
  const closeMobile = () => setMobileOpen(false);

  // Notification helpers
  const unread = list.filter((n) => !n.read).length;
  const latest5 = list.slice(0, 5); // Show only the latest 5 notifications

  // Shared NavLink class styling (active state vs hover)
  const navClass = ({ isActive }) =>
    `px-3 py-1 rounded transition ${
      isActive ? 'bg-blue-600 text-white' : 'hover:bg-gray-700'
    }`;

  // Links shown only to users
  const userLinks = (
    <>
      <NavLink to="/locations" className={navClass} onClick={closeMobile}>
        Locations
      </NavLink>
      <NavLink to="/my-reservations" className={navClass} onClick={closeMobile}>
        My Reservations
      </NavLink>
    </>
  );

  // Admin-specific links
  const adminLinks = (
    <>
      <NavLink to="/dashboard" className={navClass} onClick={closeMobile}>
        Dashboard
      </NavLink>
      <NavLink to="/admin/locations" className={navClass} onClick={closeMobile}>
        Manage Locations
      </NavLink>
      <NavLink to="/admin/users" className={navClass} onClick={closeMobile}>
        Manage Users
      </NavLink>
    </>
  );

  // Main render: navigation bar with role-based logic and dropdowns
  return (
    <nav
      className="sticky top-2 mx-2 lg:mx-auto max-w-6xl z-50
                 bg-gray-800/95 backdrop-blur-md text-white
                 px-4 py-3 rounded-lg shadow-lg"
    >
      {/* Top row: Logo, Hamburger menu (mobile), and tool strip */}
      <div className="flex justify-between items-center">
        {/* Logo always links to home */}
        <Link
          to="/"
          className="font-semibold text-lg hover:opacity-90 mr-6 md:mr-10"
          onClick={closeMobile}
        >
          Smart Parking
        </Link>

        {/* Mobile hamburger menu toggle */}
        <button
          className="md:hidden p-2 rounded hover:bg-gray-700 focus:outline-none"
          onClick={() => setMobileOpen((o) => !o)}
          aria-label="Toggle menu"
        >
          ☰
        </button>

        {/* Desktop view: navigation links + right-side tools */}
        <div className="hidden md:flex items-center gap-6">
          {/* Show links based on user role */}
          {user?.role === 'user' && userLinks}
          {user?.role === 'admin' && (asUser ? userLinks : adminLinks)}

          {/* Tool strip: Admin slider → Notifications → Profile */}
          {user && (
            <>
              {/* Admin/User toggle switch (only for admins) */}
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

              {/* Notifications dropdown with unread badge */}
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

                {/* Notification list dropdown */}
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

              {/* Profile dropdown with logout and profile view */}
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

                {/* Profile menu dropdown */}
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

      {/* Mobile dropdown menu (shown only if open) */}
      {mobileOpen && (
        <div className="md:hidden flex flex-col gap-3 mt-4 p-4 bg-gray-800 rounded-lg shadow-lg z-50">
          {/* Role-based nav links for mobile */}
          {user?.role === 'user' && userLinks}
          {user?.role === 'admin' && (asUser ? userLinks : adminLinks)}
          <hr className="border-gray-700" />

          {/* Admin tools in mobile view */}
          {user && (
            <>
              {/* Admin/User switch (mobile) */}
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

              {/* Notifications button (mobile) */}
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

              {/* Profile link and logout (mobile) */}
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
