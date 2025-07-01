/* ------------------------------------------------------------------
   api.js
   Tiny fetch wrapper that automatically adds JWT headers and works
   in dev (*relative /api*) and prod (full Render URL).
-------------------------------------------------------------------*/

import { useMemo } from 'react';
import { useAuth } from '../context/AuthContext';

/* 🔑 1. Pick API base URL
      • In production Render injects VITE_BACKEND_PROXY.
      • Locally we fall back to '/api' so Vite dev‑server proxy works. */
const BASE =
  import.meta.env.VITE_BACKEND_PROXY  // e.g. https://ingen-parking-backend.onrender.com/api
  || '/api';                          // dev fallback

/* ---------------------------------------------------------- */
/*  Centralised fetch error handler                           */
/* ---------------------------------------------------------- */
async function handleResponse(res) {
  const contentType = res.headers.get('content-type') || '';
  const isJson = contentType.includes('application/json');

  if (!res.ok) {
    // Try to read server‑provided error
    const body = isJson ? await res.json().catch(() => null)
                        : await res.text();
    const message =
      typeof body === 'string' ? body            // plain‑text error
                               : body?.error || 'Request failed';

    throw new Error(message);                    // Bubble up to caller
  }

  // 204 No‑Content should return something truthy
  if (res.status === 204) return {};
  return isJson ? res.json() : res.text();
}

/* ---------------------------------------------------------- */
/*  `useApi` hook – stable client across re‑renders           */
/* ---------------------------------------------------------- */
export const useApi = () => {
  const { token } = useAuth();           // JWT from context

  /* `useMemo` ensures we return the same client object
     until the JWT token actually changes. */
  return useMemo(() => {
    const commonHeaders = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };

    // Helper to assemble fetch options
    const opts = (method, body) => ({
      method,
      headers: commonHeaders,
      ...(body ? { body: JSON.stringify(body) } : {}),
    });

    /* Expose the four common verbs.
       1st arg: endpoint path (e.g. '/auth/login')
       2nd arg: JSON body (POST/PUT only) */
    return {
      get:  (url)        => fetch(`${BASE}${url}`, opts('GET'))
                             .then(handleResponse),
      post: (url, body)  => fetch(`${BASE}${url}`, opts('POST', body))
                             .then(handleResponse),
      put:  (url, body)  => fetch(`${BASE}${url}`, opts('PUT', body))
                             .then(handleResponse),
      del:  (url)        => fetch(`${BASE}${url}`, opts('DELETE'))
                             .then(handleResponse),
    };
  }, [token]); // ← Recreates client only when JWT token changes
};
