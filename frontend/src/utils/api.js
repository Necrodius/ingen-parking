import { useAuth } from '../context/AuthContext';

/* Factory returns a tiny wrapper around fetch */
export function apiFactory(token) {
  const base = '/api';           // served via Vite proxy

  const defaultHeaders = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}), // ← attaches JWT
  };

  return {
    get:  (url)       => fetch(base + url, { headers: defaultHeaders }),
    post: (url, body) => fetch(base + url, { method: 'POST', headers: defaultHeaders, body: JSON.stringify(body) }),
    put:  (url, body) => fetch(base + url, { method: 'PUT',  headers: defaultHeaders, body: JSON.stringify(body) }),
    del:  (url)       => fetch(base + url, { method: 'DELETE', headers: defaultHeaders }),
  };
}

/* React hook so components always get a helper with the
   *current* token from context                           */
export const useApi = () => {
  const { token } = useAuth();
  return apiFactory(token);
};
