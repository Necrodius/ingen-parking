// Simple helpers for <input type="datetime-local"> ↔ UTC ISO strings
// ----------------------------------------------------------------

// turn "2025‑07‑01T13:00" (local) → "2025‑07‑01T05:00:00.000Z"
export const localInputToIso = (localStr = '') => {
  if (!localStr) return '';
  return new Date(localStr).toISOString();
};

// turn "2025‑07‑01T05:00:00.000Z" → "2025‑07‑01T13:00" (local)
export const isoToLocalInput = (iso = '') => {
  if (!iso) return '';
  return new Date(iso).toISOString().slice(0, 16);   // "YYYY‑MM‑DDTHH:mm"
};
