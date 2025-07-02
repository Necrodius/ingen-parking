import { createContext, useContext, useEffect, useMemo, useState } from 'react';

const AuthCtx = createContext(null);

/*  Utility: decode a JWT payload */
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

/*  Context Provider */
export function AuthProvider({ children }) {
  /* Re‑hydrate existing token from localStorage */
  const [token, setToken] = useState(() => localStorage.getItem('token'));

  /* Derive and moise `user` object from token */
  const user = useMemo(() => decodeJwt(token), [token]);

  /* Helpers for login / logout that keep localStorage in sync */
  const login = (newToken) => {
    setToken(newToken);
    localStorage.setItem('token', newToken);
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem('token');
  };

  /* Auto‑logout once the token’s `exp` time is reached */
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

  /* Delay rendering children until the auth state is initialised */
  const [ready, setReady] = useState(false);
  useEffect(() => setReady(true), []);

  return (
    <AuthCtx.Provider value={{ token, user, login, logout }}>
      {ready && children}
    </AuthCtx.Provider>
  );
}

/*  Convenience hook */
export const useAuth = () => useContext(AuthCtx);
