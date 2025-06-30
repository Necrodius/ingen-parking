import { useEffect, useState } from 'react';
import { useApi } from '../utils/api';
import { toast } from 'react-hot-toast';

export default function MyReservations() {
  const api = useApi();

  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState('');

  // Load reservations once
  const load = async () => {
    setLoading(true);
    setErr('');
    try {
      const { reservations } = await api.get('/reservation/reservations');
      setReservations(reservations);
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const cancel = async (id) => {
    try {
      await api.post(`/reservation/reservations/${id}/cancel`);
      toast.success('Reservation cancelled');
      load(); // reload list
    } catch (e) {
      toast.error(e.message);
    }
  };

  // UI render
  if (loading) return <p className="p-4">Loading…</p>;
  if (err) return <p className="p-4 text-red-600">{err}</p>;

  return (
    <section className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">My Reservations</h1>

      <div className="overflow-x-auto">
        <table className="min-w-full border rounded">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-2 text-left">Slot</th>
              <th className="px-4 py-2 text-left">Start</th>
              <th className="px-4 py-2 text-left">End</th>
              <th className="px-4 py-2 text-left">Status</th>
              <th className="px-4 py-2" />
            </tr>
          </thead>
          <tbody>
            {reservations.map((r) => (
              <tr key={r.id} className="border-t">
                <td className="px-4 py-2">{r.slot_label}</td>
                <td className="px-4 py-2">
                  {new Date(r.start_ts).toLocaleString()}
                </td>
                <td className="px-4 py-2">
                  {new Date(r.end_ts).toLocaleString()}
                </td>
                <td className="px-4 py-2">{r.status}</td>
                <td className="px-4 py-2 text-right">
                  {['booked', 'ongoing'].includes(r.status) && (
                    <button
                      onClick={() => cancel(r.id)}
                      className="text-red-600 hover:underline"
                    >
                      Cancel
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
