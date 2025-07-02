// src/pages/Slots.jsx
/*
  💡  SLOT LIST + BOOKING (availability derived from reservations)
  ────────────────────────────────────────────────────────────────
  • No more reliance on a persisted `is_available` column.
  • We fetch current‑window reservations and mark slots with a
    local boolean `taken` (true = occupied / false = free).
  • Filtering, pagination, and booking flow stay the same.
*/

import { useEffect, useState, useCallback, useMemo } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';

import { useApi } from '../utils/api';
import { useNotifications } from '../context/NotificationContext';
import { localInputToIso, isoToLocalInput } from '../utils/datetime';

export default function Slots() {
  /* ───────── Routing & Context ───────── */
  const { id: locationId }     = useParams();             // /:id param
  const { state: loc }         = useLocation();           // { name, address }
  const navigate               = useNavigate();
  const api                    = useApi();
  const { notify }             = useNotifications();

  /* ───────── Component State ───────── */
  const [slots, setSlots]           = useState([]);       // decorated with { taken }
  const [loading, setLoading]       = useState(false);
  const [err, setErr]               = useState('');

  /* date‑range filter (Asia/Manila local) */
  const [fStart, setFStart]         = useState('');
  const [fEnd, setFEnd]             = useState('');

  /* booking modal */
  const [show, setShow]             = useState(false);
  const [activeSlot, setActive]     = useState(null);
  const [startTs, setStartTs]       = useState('');
  const [endTs, setEndTs]           = useState('');

  /* desktop pagination */
  const [page, setPage]             = useState(0);
  const [pageSize, setPageSize]     = useState(Infinity);
  const [isWide, setIsWide]         = useState(() => window.innerWidth >= 1024);

  /* ───────── Helpers ───────── */
  /* recompute pageSize on resize */
  const calcPageSize = () => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    const HEADER = 270;   // header + filter ≈ 270 px
    const CARD   = 160;   // slot‑card height

    let cols = 1;               // mobile default
    if (w >= 1024) cols = 4;
    else if (w >= 768) cols = 3;
    else if (w >= 640) cols = 2;

    const rows = Math.max(1, Math.floor((h - HEADER) / CARD));

    setPageSize(cols * rows);
    setIsWide(w >= 1024);
  };

  useEffect(() => {
    calcPageSize();                                // on mount
    window.addEventListener('resize', calcPageSize);
    return () => window.removeEventListener('resize', calcPageSize);
  }, []);

  /* decorate slot array with `taken` flag */
  const markTaken = (slotArr, reservationsArr) => {
    const takenIds = new Set(reservationsArr.map(r => r.slot_id));
    return slotArr.map(s => ({ ...s, taken: takenIds.has(s.id) }));
  };

  /* fetch all slots + *current* reservations (for "now") */
  const loadAllSlots = useCallback(async () => {
    setLoading(true); setErr('');
    try {
      const [{ slots: rawSlots }, { reservations }] = await Promise.all([
        api.get(`/parking_slot/slots?location_id=${locationId}`),
        api.get(
          `/reservation/reservations?location_id=${locationId}`
          + `&start_ts=${encodeURIComponent(new Date().toISOString())}`
          + `&end_ts=${encodeURIComponent(new Date().toISOString())}`
        ),
      ]);
      setSlots(markTaken(rawSlots, reservations));
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  }, [api, locationId]);

  /* filter by availability within a custom window */
  const applyFilter = useCallback(async () => {
    if (!fStart || !fEnd) return;

    const qs =
      `?location_id=${locationId}`
      + `&start_ts=${encodeURIComponent(localInputToIso(fStart))}`
      + `&end_ts=${encodeURIComponent(localInputToIso(fEnd))}`;

    setLoading(true); setErr('');
    try {
      const [{ slots: rawSlots }, { reservations }] = await Promise.all([
        api.get(`/parking_slot/slots${qs}`),
        api.get(`/reservation/reservations${qs}`),
      ]);
      setSlots(markTaken(rawSlots, reservations));
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  }, [api, fStart, fEnd, locationId]);

  /* clear filter back to "now" view */
  const clearFilter = () => { setFStart(''); setFEnd(''); loadAllSlots(); };

  /* reset to first page whenever the data‑set or layout changes */
  useEffect(() => setPage(0), [slots.length, pageSize, isWide]);

  /* slice for current page (desktop) */
  const pagedSlots = useMemo(
    () => (isWide
      ? slots.slice(page * pageSize, page * pageSize + pageSize)
      : slots),
    [slots, page, pageSize, isWide],
  );

  const totalPages = isWide ? Math.ceil(slots.length / pageSize) : 1;

  /* initial load */
  useEffect(() => { loadAllSlots(); }, [locationId, loadAllSlots]);

  /* open booking modal if the slot is still free */
  const openBooking = (slot) => {
    if (slot.taken) return;                    // sanity‑guard
    setActive(slot);

    const now = new Date();
    const dS  = fStart ? new Date(fStart) : now;
    const dE  = fEnd
      ? new Date(fEnd)
      : new Date(now.getTime() + 2 * 60 * 60 * 1000); // +2 h default

    setStartTs(isoToLocalInput(dS.toISOString()));
    setEndTs  (isoToLocalInput(dE.toISOString()));
    setShow(true);
  };

  /* confirm booking */
  const handleBook = async () => {
    if (new Date(endTs) <= new Date(startTs)) {
      toast.error('End time must be after start time'); return;
    }
    try {
      await api.post('/reservation/reservations', {
        slot_id : activeSlot.id,
        start_ts: localInputToIso(startTs),
        end_ts  : localInputToIso(endTs),
      });
      notify('Reservation confirmed!');
      // mark it taken *locally* so UI updates immediately
      setSlots(prev => prev.map(
        s => (s.id === activeSlot.id ? { ...s, taken: true } : s),
      ));
      closeModal();
    } catch (e) {
      toast.error(e.message);
    }
  };

  /* close modal helper */
  const closeModal = () => { setShow(false); setActive(null); };

  /* ───────── UI ───────── */
  return (
    <main className="relative min-h-screen flex flex-col items-center bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 text-white overflow-hidden p-6">
      {/* grain layer */}
      <div className="pointer-events-none absolute inset-0 opacity-[0.06] mix-blend-overlay bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjYwIiBoZWlnaHQ9IjYwIiBmaWxsPSIjZmZmIi8+PGNpcmNsZSBmaWxsPSIjZGRkIiByPSIxIiBjeD0iMTIiIGN5PSI2Ii8+PGNpcmNsZSBmaWxsPSIjZGRkIiByPSIxIiBjeD0iMjQiIGN5PSIyMCIvPjxjaXJjbGUgZmlsbD0iI2RkZCIgcj0iMSIgY3g9IjQ1IiBjeT0iMzUiLz48L3N2Zz4=')" />

      {/* aesthetic blobs */}
      <div className="absolute -top-40 -left-32 w-[28rem] h-[28rem] bg-indigo-400 rounded-full opacity-20 blur-[120px]" />
      <div className="absolute -bottom-40 -right-32 w-[34rem] h-[34rem] bg-pink-500 rounded-full opacity-20 blur-[120px]" />

      {/* back link */}
      <button onClick={() => navigate(-1)} className="relative z-10 self-start text-blue-200 hover:text-white">
        ← Back
      </button>

      {/* outer container */}
      <div className="relative z-10 w-full max-w-6xl mt-6 h-[85vh] p-8 flex flex-col backdrop-blur-md bg-white/10 border border-white/20 rounded-3xl shadow-2xl">
        {/* header + filter */}
        <header>
          <h1 className="text-3xl sm:text-4xl font-extrabold drop-shadow-lg">
            {loc?.name || 'Parking Location'}
          </h1>
          <p className="text-indigo-100">{loc?.address}</p>
        </header>

        <div className="mt-4 flex flex-wrap items-end gap-2 text-sm">
          {/* start datetime */}
          <label className="flex flex-col">
            <span className="sr-only">Start</span>
            <input
              type="datetime-local"
              className="rounded-lg border border-white/20 bg-white/90 text-blue-700 px-2 py-1 text-xs"
              value={fStart}
              onChange={e => setFStart(e.target.value)}
            />
          </label>

          <span className="hidden sm:inline text-gray-300">—</span>

          {/* end datetime */}
          <label className="flex flex-col">
            <span className="sr-only">End</span>
            <input
              type="datetime-local"
              className="rounded-lg border border-white/20 bg-white/90 text-blue-700 px-2 py-1 text-xs"
              value={fEnd}
              onChange={e => setFEnd(e.target.value)}
            />
          </label>

          {/* filter */}
          <button
            onClick={applyFilter}
            disabled={!fStart || !fEnd}
            className="rounded-lg px-3 py-1 text-xs text-white bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
          >
            Filter
          </button>

          {/* clear */}
          {(fStart || fEnd) && (
            <button
              onClick={clearFilter}
              className="rounded-lg bg-gray-200/40 backdrop-blur px-3 py-1 text-xs hover:bg-gray-200/60 transition"
            >
              Clear
            </button>
          )}

          {/* API error */}
          {err && <span className="text-xs text-red-300">{err}</span>}
        </div>

        {/* slot list: scroll mobile / paginate desktop */}
        <div className={`mt-6 flex-1 ${!isWide ? 'overflow-y-auto pr-2 [&::-webkit-scrollbar]:hidden scrollbar-width-none' : ''}`}>
          {loading && <p className="text-indigo-100">Loading…</p>}
          {!loading && pagedSlots.length === 0 && (
            <p className="text-indigo-100">No available slots for the current view.</p>
          )}

          {/* grid of slot cards */}
          <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {pagedSlots.map(s => (
              <div
                key={s.id}
                className={`p-4 rounded-2xl shadow flex flex-col justify-between transition ${
                  s.taken
                    ? 'bg-gray-100/50 text-gray-500 border border-gray-300 opacity-60'
                    : 'bg-white text-blue-700 border-2 border-green-500 hover:shadow-lg'
                }`}
              >
                <span className="font-mono text-lg">Slot {s.slot_label}</span>

                {!s.taken ? (
                  <button
                    onClick={() => openBooking(s)}
                    className="mt-3 px-3 py-1 rounded bg-green-600 text-white hover:bg-green-700"
                  >
                    Book
                  </button>
                ) : (
                  <span className="mt-3 text-sm">Occupied</span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* pagination (desktop) */}
        {isWide && totalPages > 1 && (
          <div className="mt-4 flex justify-center items-center gap-4 text-sm">
            <button
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-3 py-1 rounded-lg border hover:bg-white/20 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              ⬅ Prev
            </button>

            <span>Page {page + 1} / {totalPages}</span>

            <button
              onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
              disabled={page === totalPages - 1}
              className="px-3 py-1 rounded-lg border hover:bg-white/20 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Next ➡
            </button>
          </div>
        )}
      </div>

      {/* booking modal */}
      {show && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={closeModal}>
          <div
            className="w-full max-w-sm rounded-3xl backdrop-blur-md bg-white/90 p-8 shadow-2xl"
            onClick={e => e.stopPropagation()} /* outside click closes */
          >
            <h2 className="mb-4 text-xl font-semibold text-blue-700">
              Book Slot {activeSlot.slot_label}
            </h2>

            <div className="space-y-4">
              {/* start */}
              <label className="block text-sm font-medium text-blue-700">
                Start
                <input
                  type="datetime-local"
                  className="mt-1 w-full rounded-lg border px-3 py-2"
                  value={startTs}
                  onChange={e => setStartTs(e.target.value)}
                />
              </label>

              {/* end */}
              <label className="block text-sm font-medium text-blue-700">
                End
                <input
                  type="datetime-local"
                  className="mt-1 w-full rounded-lg border px-3 py-2"
                  value={endTs}
                  onChange={e => setEndTs(e.target.value)}
                />
              </label>

              <div className="mt-6 flex justify-end gap-3">
                <button onClick={closeModal} className="rounded-lg bg-gray-200 px-4 py-2 hover:bg-gray-300">
                  Cancel
                </button>
                <button onClick={handleBook} className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700">
                  Confirm
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
