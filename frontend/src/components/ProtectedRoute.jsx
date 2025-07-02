import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function ProtectedRoute({ children, roles }) {
  const { token, user } = useAuth(); // Destructure auth token and user info (including role)

  /* If no valid token is found, redirect to the login page. */
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  /* If roles are specified, check that the user's role matches one of them */
  if (roles && !roles.includes(user?.role)) {
    return <Navigate to="/" replace />;
  }

  /* If authenticated then render protected content */
  return children;
}
