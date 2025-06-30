import { useAuth } from '../context/AuthContext';
import { Link, NavLink, useNavigate } from 'react-router-dom';

export default function Nav() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();                 // clears context + localStorage
    navigate('/login');
  };

  const linkStyle = 'hover:underline px-3';

  return (
    <nav className="bg-gray-800 text-white p-4 flex justify-between items-center">
      {/* ───── Left side logo + links ───── */}
      <div className="flex items-center space-x-4">
        <Link to="/" className="font-semibold text-lg">
          Smart Parking
        </Link>

        {/* Links for regular users */}
        {user?.role === 'user' && (
          <>
            <NavLink to="/locations" className={linkStyle}>
              Locations
            </NavLink>
            <NavLink to="/my-reservations" className={linkStyle}>
              My Reservations
            </NavLink>
          </>
        )}

        {/* Links for admins (optional) */}
        {user?.role === 'admin' && (
          <>
            <NavLink to="/dashboard" className={linkStyle}>
              Dashboard
            </NavLink>
            <NavLink to="/admin/locations" className={linkStyle}>
              Manage Locations
            </NavLink>
            {/* Add more admin links as needed */}
          </>
        )}

        {/* Profile link for ANY logged‑in user */}
        {user && (
          <NavLink to="/profile" className={linkStyle}>
            Profile
          </NavLink>
        )}
      </div>

      {/* ───── Right side logout ───── */}
      {user && (
        <button
          onClick={handleLogout}
          className="bg-red-500 hover:bg-red-600 px-3 py-1 rounded"
        >
          Logout
        </button>
      )}
    </nav>
  );
}
