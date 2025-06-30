/*
  Slots.jsx
  ───────────────────────────────────────────────────────────
  • Lists slots for the selected parking location.
  • Clicking an available slot opens a modal with
    "Start" and "End" datetime‑pickers.
  • On submit → POST /reservation/reservations
      { slot_id, start_ts, end_ts }
  • After success, slot flips to Occupied and toast fires.
*/

import { useEffect, useState } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { useApi } from '../utils/api';
import { toast } from 'react-hot-toast';

export default function Slots() {
  /* ───────── route + helpers ───────── */
  const { id: locationId }  = useParams();
  const { state: loc }      = useLocation();   // passed from Locations.jsx
  const navigate            = useNavigate();
  const api                 = useApi();

  /* ───────── slot list state ───────── */
  const [slots, setSlots] = useState([]);
  const [err,   setErr]   = useState('');
  const [loading, setLoading] = useState(true);

  /* ───────── modal state ───────── */
  const [show, setShow]           = useState(false);
  const [activeSlot, setActive]   = useState(null);
  const [startTs, setStartTs]     = useState('');
  const [endTs,   setEndTs]       = useState('');

  /* --- fetch slots once on mount --- */
  useEffect(() => {
    (async () => {
      try {
        const { slots } = await api.get(
          `/parking_slot/slots?location_id=${locationId}`
        );
        setSlots(slots);
      } catch (e) {
        setErr(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, [api, locationId]);

  /* ───────── open modal ───────── */
  const openBooking = (slot) => {
    setActive(slot);
    const now   = new Date();
    const plus2 = new Date(now.getTime() + 2 * 60 * 60 * 1000);

    // HTML datetime‑local wants "YYYY‑MM‑DDTHH:mm"
    const pad  = (n) => n.toString().padStart(2, '0');
    const fmt  = (d) =>
      `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(
        d.getDate()
      )}T${pad(d.getHours())}:${pad(d.getMinutes())}`;

    setStartTs(fmt(now));
    setEndTs(fmt(plus2));
    setShow(true);
  };

  /* ───────── handle booking ───────── */
  const handleBook = async () => {
    if (new Date(endTs) <= new Date(startTs)) {
      toast.error('End time must be after start time');
      return;
    }
    try {
      await api.post('/reservation/reservations', {
        slot_id: activeSlot.id,
        start_ts: new Date(startTs).toISOString(),
        end_ts:   new Date(endTs).toISOString(),
      });
      toast.success('Reservation confirmed!');
      // Mark slot as occupied locally
      setSlots((prev) =>
        prev.map((s) =>
          s.id === activeSlot.id ? { ...s, is_available: false } : s
        )
      );
      closeModal();
    } catch (e) {
      toast.error(e.message);
    }
  };

  /* ───────── close modal helper ───────── */
  const closeModal = () => {
    setShow(false);
    setActive(null);
  };

  /* ───────── UI states ───────── */
  if (loading) return <p className="p-4">Loading…</p>;
  if (err)     return <p className="p-4 text-red-600">{err}</p>;

  return (
    <section className="p-6 space-y-4">
      <button onClick={() => navigate(-1)} className="text-blue-600">
        &larr; Back
      </button>

      {/* Location header */}
      <h1 className="text-2xl font-bold">{loc?.name || 'Parking Location'}</h1>
      <p className="text-gray-600">{loc?.address}</p>

      {/* Slot grid */}
      <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {slots.map((s) => (
          <div
            key={s.id}
            className={`p-4 border rounded-xl flex flex-col justify-between ${
              s.is_available ? 'border-green-500' : 'border-gray-300 opacity-60'
            }`}
          >
            <span className="font-mono text-lg">Slot {s.slot_label}</span>
            {s.is_available ? (
              <button
                onClick={() => openBooking(s)}
                className="mt-2 px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
              >
                Book
              </button>
            ) : (
              <span className="text-sm text-gray-500 mt-2">Occupied</span>
            )}
          </div>
        ))}
      </div>

      {/* ───────── Modal ───────── */}
      {show && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
          onClick={closeModal}
        >
          <div
            className="w-full max-w-sm rounded-2xl bg-white p-6"
            onClick={(e) => e.stopPropagation()} // stop backdrop close
          >
            <h2 className="mb-4 text-xl font-semibold">
              Book Slot {activeSlot.slot_label}
            </h2>

            {/* start / end inputs */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium">Start</label>
                <input
                  type="datetime-local"
                  className="mt-1 w-full rounded border px-3 py-2"
                  value={startTs}
                  onChange={(e) => setStartTs(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium">End</label>
                <input
                  type="datetime-local"
                  className="mt-1 w-full rounded border px-3 py-2"
                  value={endTs}
                  onChange={(e) => setEndTs(e.target.value)}
                />
              </div>

              {/* Action buttons */}
              <div className="mt-6 flex justify-end gap-3">
                <button
                  onClick={closeModal}
                  className="rounded bg-gray-200 px-4 py-2"
                >
                  Cancel
                </button>
                <button
                  onClick={handleBook}
                  className="rounded bg-blue-600 px-4 py-2 text-white"
                >
                  Confirm
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
