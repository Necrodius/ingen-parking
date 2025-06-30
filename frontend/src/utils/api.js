/*
  api.js
  Tiny fetch wrapper that automatically adds JWT headers.

  ✨  WHAT CHANGED
  ─────────────────────────────────────────────────────────────
  • Wrapped the returned client object in React.useMemo(…) so
    its reference is stable across re‑renders.
  • Only re‑creates when the JWT token changes.
*/

import { useMemo } from 'react';
import { useAuth } from '../context/AuthContext';

/* ---------------------------------------------------------- */
/*  Centralized fetch error handler                           */
/* ---------------------------------------------------------- */
async function handleResponse(res) {
  const contentType = res.headers.get('content-type') || '';
  const isJson = contentType.includes('application/json');

  if (!res.ok) {
    const errorBody = isJson
      ? await res.json().catch(() => null)
      : await res.text();

    const message =
      typeof errorBody === 'string'
        ? errorBody
        : errorBody?.error || 'Request failed';

    throw new Error(message);
  }

  if (res.status === 204) return {};       // 204 No Content
  return isJson ? res.json() : res.text(); // Parsed JSON or plain text
}

/* ---------------------------------------------------------- */
/*  Hook that returns a stable ‘api’ client                   */
/* ---------------------------------------------------------- */
export const useApi = () => {
  const { token } = useAuth();           // JWT from context
  const BASE = '/api';                   // Vite proxy → backend

  /*  Memoise the client so *all* components that import it
      get the same reference until the token changes.        */
  return useMemo(() => {
    const commonHeaders = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };

    // Helper to build fetch options
    const opts = (method, body) => ({
      method,
      headers: commonHeaders,
      ...(body ? { body: JSON.stringify(body) } : {}),
    });

    return {
      get: (url) => fetch(BASE + url, opts('GET')).then(handleResponse),
      post: (url, body) =>
        fetch(BASE + url, opts('POST', body)).then(handleResponse),
      put: (url, body) =>
        fetch(BASE + url, opts('PUT', body)).then(handleResponse),
      del: (url) => fetch(BASE + url, opts('DELETE')).then(handleResponse),
    };
  }, [token]); // 🔑 Re‑create only when the JWT token changes
};
