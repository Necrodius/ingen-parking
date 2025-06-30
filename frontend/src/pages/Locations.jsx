// List every parking location and link to its slots page
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useApi } from '../utils/api';

export default function Locations() {
  const api = useApi();
  const [locs, setLocs] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const { locations } = await api.get('/parking_location/locations'); // ✅ no trailing slash
        setLocs(locations);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    })();
  }, [api]);

  if (loading) return <p className="p-4">Loading locations…</p>;
  if (error) return <p className="p-4 text-red-600">{error}</p>;

  return (
    <section className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">Parking Locations</h1>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {locs.map((l) => (
          <Link
            key={l.id}
            to={`/locations/${l.id}/slots`}
            state={l} // 👈 pass full location object to next page
            className="block p-4 border rounded-xl shadow hover:shadow-md hover:bg-gray-50 transition"
          >
            <h2 className="text-lg font-semibold">{l.name}</h2>
            <p className="text-sm text-gray-600">{l.address}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
