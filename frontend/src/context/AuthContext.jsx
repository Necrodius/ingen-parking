import { createContext, useContext, useEffect, useState } from 'react';

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  /* ❶  Re‑hydrate once from localStorage */
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [ready, setReady] = useState(false);

  const login = (t) => {
    setToken(t);
    localStorage.setItem('token', t);
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem('token');
  };

  /* ❷  Tell the tree we’re ready (one tick) */
  useEffect(() => setReady(true), []);

  return (
    <AuthCtx.Provider value={{ token, login, logout }}>
      {ready && children}
    </AuthCtx.Provider>
  );
}

export const useAuth = () => useContext(AuthCtx);
