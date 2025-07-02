/* Fetch wrapper that adds JWT headers */

import { useMemo } from 'react';
import { useAuth } from '../context/AuthContext';

const BASE = import.meta.env.VITE_BACKEND_URL;

/* Centralised fetch error handler */
async function handleResponse(res) {
  const contentType = res.headers.get('content-type') || '';
  const isJson = contentType.includes('application/json');

  if (!res.ok) {
    /* Try to read server‑provided error */
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

/* useApi hook */
export const useApi = () => {
  const { token } = useAuth();

  /* ensures we return the same client object until the JWT token changes */
  return useMemo(() => {
    const commonHeaders = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };

    /* Helper to assemble fetch options */
    const opts = (method, body) => ({
      method,
      headers: commonHeaders,
      ...(body ? { body: JSON.stringify(body) } : {}),
    });

    /* Expose get, post, put, del */
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
  }, [token]); // Recreates client only when JWT token changes
};
