/**
 * AuthContext
 *
 * Provides global authentication state and helpers:
 * - Persists the JWT in localStorage for page refresh survival.
 * - Exposes `user` (decoded payload), `token`, `login`, and `logout`.
 * - Automatically logs the user out when the token expires.
 *
 * Usage:
 *   <AuthProvider> …children… </AuthProvider>
 *   const { user, login, logout } = useAuth();
 */

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

const AuthCtx = createContext(null);

/* ------------------------------------------------------------------ */
/*  Utility: decode a JWT payload (base64url → JSON)                  */
/* ------------------------------------------------------------------ */
function decodeJwt(token) {
  if (!token) return null;

  try {
    // JWT structure: header.payload.signature → we need the payload
    const payloadPart = token.split('.')[1];
    const json = atob(payloadPart.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(json);
  } catch {
    // Malformed token or unexpected data
    return null;
  }
}

/* ------------------------------------------------------------------ */
/*  Context Provider                                                  */
/* ------------------------------------------------------------------ */
export function AuthProvider({ children }) {
  /* Step 1:  Re‑hydrate existing token from localStorage (runs once) */
  const [token, setToken] = useState(() => localStorage.getItem('token'));

  /* Step 2:  Derive `user` object from token; memoised for efficiency */
  const user = useMemo(() => decodeJwt(token), [token]);

  /* Step 3:  Helpers for login / logout that keep localStorage in sync */
  const login = (newToken) => {
    setToken(newToken);
    localStorage.setItem('token', newToken);
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem('token');
  };

  /* Step 4:  Auto‑logout once the token’s `exp` time is reached */
  useEffect(() => {
    // Guard: if token has no exp claim, skip scheduling
    if (!user?.exp) return;

    const nowSec = Date.now() / 1000;

    // If token is already stale, log out immediately
    if (user.exp < nowSec) {
      logout();
      return;
    }

    // Otherwise schedule a logout for one second after expiry
    const timeout = setTimeout(logout, (user.exp - nowSec + 1) * 1000);
    return () => clearTimeout(timeout); // Clean up if token changes
  }, [user]); // Re‑run if `user` (i.e., token) changes

  /* Step 5:  Delay rendering children until the auth state is initialised */
  const [ready, setReady] = useState(false);
  useEffect(() => setReady(true), []);

  return (
    <AuthCtx.Provider value={{ token, user, login, logout }}>
      {ready && children}
    </AuthCtx.Provider>
  );
}

/* ------------------------------------------------------------------ */
/*  Convenience hook                                                  */
/* ------------------------------------------------------------------ */
export const useAuth = () => useContext(AuthCtx);
