import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * ProtectedRoute
 * 
 * A wrapper component that restricts access to certain routes based on authentication
 * and (optionally) the user's role.
 *
 * Usage examples:
 *   <ProtectedRoute>...</ProtectedRoute>                   // Requires any authenticated user
 *   <ProtectedRoute roles={['admin']}>...</ProtectedRoute> // Requires user to be an admin
 *
 * Props:
 * - children: JSX content to render if access is allowed
 * - roles (optional): an array of allowed roles (e.g., ['admin', 'user'])
 */
export default function ProtectedRoute({ children, roles }) {
  const { token, user } = useAuth(); // Destructure auth token and user info (including role)

  /**
   * Step 1: Require authentication
   * If no valid token is found, redirect to the login page.
   */
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  /**
   * Step 2: Optional role-based authorization
   * If roles are specified, check that the user's role matches one of them.
   * If not authorized, redirect to home (or replace with a proper 403 page).
   */
  if (roles && !roles.includes(user?.role)) {
    return <Navigate to="/" replace />;
  }

  // User is authenticated (and authorized, if applicable) → render protected content
  return children;
}
