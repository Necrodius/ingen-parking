/* --------------------------------------------------------------------------
   Slots.jsx – v9  (scrollbar‑less scrolling + mobile / desktop logic)
   --------------------------------------------------------------------------
   🚀  New in this version
   •  Added a small *utility CSS rule* (injected once on mount) that hides
      scrollbars across all modern browsers while keeping scrolling enabled.
   •  Applied that CSS class (`no-scrollbar`) to the mobile scroll container.
   •  Everything else stays identical to v8.
   -------------------------------------------------------------------------- */

import { useEffect, useState } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { useApi } from '../utils/api';
import { toast } from 'react-hot-toast';
import { useNotifications } from '../context/NotificationContext';
import { localInputToIso, isoToLocalInput } from '../utils/datetime';

export default function Slots() {
  /* ───────────────────────── Routing & Context ─────────────────────── */
  const { id: locationId } = useParams();       // parking‑location ID from URL
  const { state: loc }     = useLocation();     // { name, address } forwarded
  const navigate           = useNavigate();
  const api                = useApi();
  const { notify }         = useNotifications();

  /* ───────────────────────── Component State ───────────────────────── */
  const [slots,   setSlots]   = useState([]);         // all/filtered slots
  const [loading, setLoading] = useState(false);      // network spinner
  const [err,     setErr]     = useState('');         // API error message

  /* optional availability‑filter inputs (Asia/Manila local values) */
  const [fStart, setFStart] = useState('');
  const [fEnd,   setFEnd]   = useState('');

  /* booking modal state */
  const [show,       setShow]    = useState(false);   // modal open?
  const [activeSlot, setActive]  = useState(null);    // slot being booked
  const [startTs,    setStartTs] = useState('');      // booking start
  const [endTs,      setEndTs]   = useState('');      // booking end

  /* desktop pagination */
  const [page,     setPage]     = useState(0);        // current page #
  const [pageSize, setPageSize] = useState(Infinity); // items per page
  const [isWide,   setIsWide]   = useState(() => window.innerWidth >= 1024);

  /* ───────────────────── Inject “no‑scrollbar” CSS once ────────────── */
  useEffect(() => {
    /* Create a <style> tag that hides scrollbars for .no-scrollbar */
    const style = document.createElement('style');
    style.innerHTML = `
      .no-scrollbar::-webkit-scrollbar { display: none; } /* Chrome/Safari */
      .no-scrollbar {                                     /* Firefox/Edge  */
        -ms-overflow-style: none;    /* Edge / IE */
        scrollbar-width: none;       /* Firefox   */
      }`;
    document.head.appendChild(style);
    /* Clean‑up on unmount */
    return () => document.head.removeChild(style);
  }, []); // run only once when component mounts

  /* ───────────────────────── Data helpers ──────────────────────────── */
  /* fetch *all* slots for this parking location */
  const loadAllSlots = async () => {
    setLoading(true);
    setErr('');
    try {
      const { slots } = await api.get(`/parking_slot/slots?location_id=${locationId}`);
      setSlots(slots);                            // store API data
    } catch (e) {
      setErr(e.message);                          // show error message
    } finally {
      setLoading(false);
    }
  };

  /* apply availability filter (+ overlap check w/ existing reservations) */
  const applyFilter = async () => {
    /* guard‑clause: both start & end must be chosen */
    if (!fStart || !fEnd) return;

    const qs =
      `?location_id=${locationId}` +
      `&start_ts=${encodeURIComponent(localInputToIso(fStart))}` +
      `&end_ts=${encodeURIComponent(localInputToIso(fEnd))}`;

    setLoading(true);
    setErr('');
    try {
      /* 1) fetch slots + 2) fetch reservations in parallel */
      const [{ slots }, { reservations }] = await Promise.all([
        api.get(`/parking_slot/slots${qs}`),
        api.get(`/reservation/reservations${qs}`),
      ]);

      /* mark slots that already have a reservation as unavailable */
      const taken = new Set(reservations.map((r) => r.slot_id));
      setSlots(slots.map((s) => (taken.has(s.id) ? { ...s, is_available: false } : s)));
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  /* clear filter → reset inputs + reload all slots */
  const clearFilter = () => {
    setFStart('');
    setFEnd('');
    loadAllSlots();
  };

  /* ──────────────────────── Pagination helpers ─────────────────────── */
  /* recompute pageSize whenever window resizes (desktop only) */
  const calcPageSize = () => {
    const width  = window.innerWidth;
    const height = window.innerHeight;
    const HEADER_SPACE = 270;     // header + filter ≈ 270 px
    const CARD_H       = 160;     // slot card height (+gap)

    /* columns match our Tailwind grid breakpoints */
    let cols = 1;
    if (width >= 1024) cols = 4;
    else if (width >= 768) cols = 3;
    else if (width >= 640) cols = 2;

    /* rows that fit beneath header space */
    const rows = Math.max(1, Math.floor((height - HEADER_SPACE) / CARD_H));

    setPageSize(cols * rows);
    setIsWide(width >= 1024);     // “wide” means desktop layout
  };

  /* register resize listener once ─────────────────────────────────── */
  useEffect(() => {
    calcPageSize();                       // initial calculation
    window.addEventListener('resize', calcPageSize);
    return () => window.removeEventListener('resize', calcPageSize);
  }, []);

  /* reset to first page whenever dataset or pageSize changes ───────── */
  useEffect(() => setPage(0), [slots.length, pageSize]);

  /* pick slice of slots to show on this page (desktop) */
  const pagedSlots = isWide
    ? slots.slice(page * pageSize, page * pageSize + pageSize)
    : slots;   // on mobile we show all & rely on scrolling

  const totalPages = isWide ? Math.ceil(slots.length / pageSize) : 1;

  /* ───────────────────────── Init (load data) ─────────────────────── */
  useEffect(() => {
    loadAllSlots();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [locationId]);

  /* ───────────────────────── Booking helpers ──────────────────────── */
  /* open modal + set default start/end times */
  const openBooking = (slot) => {
    setActive(slot);

    const now      = new Date();
    const defaultS = fStart ? new Date(fStart) : now;
    const defaultE = fEnd
      ? new Date(fEnd)
      : new Date(now.getTime() + 2 * 60 * 60 * 1000); // +2h

    setStartTs(isoToLocalInput(defaultS.toISOString()));
    setEndTs  (isoToLocalInput(defaultE.toISOString()));
    setShow(true);
  };

  /* confirm booking */
  const handleBook = async () => {
    /* sanity check: end must be after start */
    if (new Date(endTs) <= new Date(startTs)) {
      toast.error('End time must be after start time');
      return;
    }
    try {
      await api.post('/reservation/reservations', {
        slot_id : activeSlot.id,
        start_ts: localInputToIso(startTs),
        end_ts  : localInputToIso(endTs),
      });
      notify('Reservation confirmed!');
      /* optimistically mark slot unavailable */
      setSlots((prev) =>
        prev.map((s) => (s.id === activeSlot.id ? { ...s, is_available: false } : s))
      );
      closeModal();
    } catch (e) {
      toast.error(e.message);
    }
  };

  /* close modal helper */
  const closeModal = () => {
    setShow(false);
    setActive(null);
  };

  /* ───────────────────────── UI ───────────────────────────────────── */
  return (
    <main className="relative min-h-screen flex flex-col items-center bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 text-white overflow-hidden p-6">
      {/* grain layer (subtle noise) */}
      <div className="pointer-events-none absolute inset-0 opacity-[0.06] mix-blend-overlay bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjYwIiBoZWlnaHQ9IjYwIiBmaWxsPSIjZmZmIi8+PGNpcmNsZSBmaWxsPSIjZGRkIiByPSIxIiBjeD0iMTIiIGN5PSI2Ii8+PGNpcmNsZSBmaWxsPSIjZGRkIiByPSIxIiBjeD0iMjQiIGN5PSIyMCIvPjxjaXJjbGUgZmlsbD0iI2RkZCIgcj0iMSIgY3g9IjQ1IiBjeT0iMzUiLz48L3N2Zz4=')]" />

      {/* decorative blurred blobs */}
      <div className="absolute -top-40 -left-32 w-[28rem] h-[28rem] bg-indigo-400 rounded-full opacity-20 blur-[120px]" />
      <div className="absolute -bottom-40 -right-32 w-[34rem] h-[34rem] bg-pink-500 rounded-full opacity-20 blur-[120px]" />

      {/* back link */}
      <button
        onClick={() => navigate(-1)}
        className="relative z-10 self-start text-blue-200 hover:text-white"
      >
        ← Back
      </button>

      {/* outer “glass” container */}
      <div
        className="relative z-10 w-full max-w-6xl mt-6 backdrop-blur-md bg-white/10 border border-white/20 rounded-3xl shadow-2xl
                   p-8 flex flex-col"
        style={{ height: '85vh' }} /* header ≈ 15vh + outer padding */
      >
        {/* ───────────── Header & Filter (static – never scroll) ───────────── */}
        <header>
          <h1 className="text-3xl sm:text-4xl font-extrabold drop-shadow-lg">
            {loc?.name || 'Parking Location'}
          </h1>
          <p className="text-indigo-100">{loc?.address}</p>
        </header>

        {/* filter bar */}
        <div className="mt-4 flex flex-wrap items-end gap-2 text-sm">
          {/* start datetime */}
          <label className="flex flex-col">
            <span className="sr-only">Start</span>
            <input
              type="datetime-local"
              className="rounded-lg border border-white/20 bg-white/90 text-blue-700 px-2 py-1 text-xs"
              value={fStart}
              onChange={(e) => setFStart(e.target.value)}
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
              onChange={(e) => setFEnd(e.target.value)}
            />
          </label>

          {/* filter */}
          <button
            onClick={applyFilter}
            disabled={!fStart || !fEnd}
            className={`rounded-lg px-3 py-1 text-xs text-white transition
              ${!fStart || !fEnd
                ? 'cursor-not-allowed bg-gray-400'
                : 'bg-green-600 hover:bg-green-700'}`}
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

          {/* API error (if any) */}
          {err && <span className="text-xs text-red-300">{err}</span>}
        </div>

        {/* ───────────── Slot List (scroll on mobile / paginate desktop) ───────────── */}
        <div
          className={`mt-6 flex-1 ${!isWide ? 'overflow-y-auto no-scrollbar pr-2' : ''}`}
        >
          {loading && <p className="text-indigo-100">Loading…</p>}

          {!loading && pagedSlots.length === 0 && (
            <p className="text-indigo-100">No available slots for the current view.</p>
          )}

          {/* grid of slot cards */}
          <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {pagedSlots.map((s) => (
              <div
                key={s.id}
                className={`p-4 rounded-2xl shadow flex flex-col justify-between transition
                  ${s.is_available
                    ? 'bg-white text-blue-700 border-2 border-green-500 hover:shadow-lg'
                    : 'bg-gray-100/50 text-gray-500 border border-gray-300 opacity-60'}`}
              >
                <span className="font-mono text-lg">Slot {s.slot_label}</span>

                {s.is_available ? (
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

        {/* pagination controls (desktop only) */}
        {isWide && totalPages > 1 && (
          <div className="mt-4 flex justify-center items-center gap-4 text-sm">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className={`px-3 py-1 rounded-lg border
                ${page === 0 ? 'opacity-40 cursor-not-allowed' : 'hover:bg-white/20'}`}
            >
              ⬅ Prev
            </button>

            <span>
              Page {page + 1} / {totalPages}
            </span>

            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page === totalPages - 1}
              className={`px-3 py-1 rounded-lg border
                ${page === totalPages - 1 ? 'opacity-40 cursor-not-allowed' : 'hover:bg-white/20'}`}
            >
              Next ➡
            </button>
          </div>
        )}
      </div>

      {/* ───────────── Booking Modal ───────────── */}
      {show && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
          onClick={closeModal}
        >
          {/* modal card */}
          <div
            className="w-full max-w-sm rounded-3xl backdrop-blur-md bg-white/90 p-8 shadow-2xl"
            onClick={(e) => e.stopPropagation()} /* stop bubbling so click outside = close */
          >
            <h2 className="mb-4 text-xl font-semibold text-blue-700">
              Book Slot {activeSlot.slot_label}
            </h2>

            <div className="space-y-4">
              {/* start datetime picker */}
              <label className="block text-sm font-medium text-blue-700">
                Start
                <input
                  type="datetime-local"
                  className="mt-1 w-full rounded-lg border px-3 py-2"
                  value={startTs}
                  onChange={(e) => setStartTs(e.target.value)}
                />
              </label>

              {/* end datetime picker */}
              <label className="block text-sm font-medium text-blue-700">
                End
                <input
                  type="datetime-local"
                  className="mt-1 w-full rounded-lg border px-3 py-2"
                  value={endTs}
                  onChange={(e) => setEndTs(e.target.value)}
                />
              </label>

              {/* action buttons */}
              <div className="mt-6 flex justify-end gap-3">
                <button
                  onClick={closeModal}
                  className="rounded-lg bg-gray-200 px-4 py-2 hover:bg-gray-300"
                >
                  Cancel
                </button>
                <button
                  onClick={handleBook}
                  className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
                >
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
