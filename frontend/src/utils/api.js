// frontend/src/utils/api.js
import { useAuth } from '../context/AuthContext';

/* ------------------------------------------------------------------ */
/*  Common fetch wrapper                                               */
/* ------------------------------------------------------------------ */
function handleResponse(res) {
  if (!res.ok) {
    // Try to read JSON; otherwise fall back to plain text
    return res
      .clone()
      .json()
      .catch(() => res.text())
      .then(msg => {
        const message = typeof msg === 'string' ? msg : msg.error || 'Request failed';
        throw new Error(message);
      });
  }
  return res.json();               // ✅ all good – already parsed
}

/* ------------------------------------------------------------------ */
/*  Hook that returns a tiny ‘api’ client                              */
/* ------------------------------------------------------------------ */
export const useApi = () => {
  const { token } = useAuth();

  const base = '/api';             // goes through Vite proxy
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  return {
    get : url            => fetch(base + url, { headers }).then(handleResponse),
    post: (url, body)    =>
      fetch(base + url, { method: 'POST', headers, body: JSON.stringify(body) })
        .then(handleResponse),
    put : (url, body)    =>
      fetch(base + url, { method: 'PUT',  headers, body: JSON.stringify(body) })
        .then(handleResponse),
    del : url            =>
      fetch(base + url, { method: 'DELETE', headers }).then(handleResponse),
  };
};
