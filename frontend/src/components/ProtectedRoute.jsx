import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * Usage:
 *   <ProtectedRoute>...</ProtectedRoute>                   // any logged‑in user
 *   <ProtectedRoute roles={['admin']}>...</ProtectedRoute> // only admins
 */
export default function ProtectedRoute({ children, roles }) {
  const { token, user } = useAuth();     // user contains role

  /* 1️⃣ must be logged in */
  if (!token) return <Navigate to="/login" replace />;

  /* 2️⃣ role‑based guard (optional) */
  if (roles && !roles.includes(user?.role)) {
    return <Navigate to="/" replace />;  // or a 403 page
  }

  return children;
}
