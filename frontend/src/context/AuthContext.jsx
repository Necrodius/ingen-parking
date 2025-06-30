import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

const AuthCtx = createContext(null);

/* ------------------------------------------------------------- */
/*  Helper – decode JWT payload (base64url → JSON)               */
/* ------------------------------------------------------------- */
function decodeJwt(token) {
  if (!token) return null;
  try {
    // token = header.payload.signature  → we want payload
    const payloadPart = token.split('.')[1];
    const json = atob(payloadPart.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(json);
  } catch {
    return null;
  }
}

/* ------------------------------------------------------------- */
/*  Provider                                                     */
/* ------------------------------------------------------------- */
export function AuthProvider({ children }) {
  /* 1️⃣  Re‑hydrate token from localStorage once */
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [ready, setReady] = useState(false);

  /* 2️⃣  Derived user object (memoised) */
  const user = useMemo(() => decodeJwt(token), [token]);

  /* 3️⃣  Login / logout helpers */
  const login = (t) => {
    setToken(t);
    localStorage.setItem('token', t);
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem('token');
  };

  /* 4️⃣  Auto‑logout if token expired */
  useEffect(() => {
    if (!user?.exp) return;

    const nowSec = Date.now() / 1000;
    if (user.exp < nowSec) {
      logout();
      return;
    }

    // schedule logout one second after expiry
    const timeout = setTimeout(logout, (user.exp - nowSec + 1) * 1000);
    return () => clearTimeout(timeout);
  }, [user]);

  /* 5️⃣  Tell tree we’re ready (one tick) */
  useEffect(() => setReady(true), []);

  return (
    <AuthCtx.Provider value={{ token, user, login, logout }}>
      {ready && children}
    </AuthCtx.Provider>
  );
}

export const useAuth = () => useContext(AuthCtx);
