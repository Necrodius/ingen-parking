import { useEffect, useMemo, useState } from 'react';
import { useApi } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-hot-toast';
import { useNotifications } from '../context/NotificationContext';

export default function MyReservations() {
  /* ──────────── context ──────────── */
  const api          = useApi();
  const { user: me } = useAuth();
  const { notify }   = useNotifications();

  const myId   = Number(me?.id ?? me?.user_id ?? me?.sub ?? NaN);
  const asUser = localStorage.getItem('sp_asUser') === 'true';

  /* ──────────── state ──────────── */
  const [reservations, setReservations] = useState([]);
  const [slotMap,      setSlotMap]      = useState({});
  const [locMap,       setLocMap]       = useState({});
  const [userMap,      setUserMap]      = useState({});
  const [filter,       setFilter]       = useState('all');
  const [loading,      setLoading]      = useState(true);
  const [err,          setErr]          = useState('');

  /* pagination */
  const [page,     setPage]     = useState(0);
  const [pageSize, setPageSize] = useState(Infinity);
  const [isWide,   setIsWide]   = useState(() => window.innerWidth >= 1024);
  const [isTiny,   setIsTiny]   = useState(() => window.innerWidth < 900);

  /* merge helper */
  const mergeUsers = (arr = []) =>
    setUserMap(prev => {
      const next = { ...prev };
      arr.forEach(u => (next[Number(u.id)] = `${u.first_name} ${u.last_name}`));
      if (!next[myId]) next[myId] = `${me.first_name ?? ''} ${me.last_name ?? ''}`.trim();
      return next;
    });

  /* resize‑aware layout */
  const calc = () => {
    const rows = Math.max(1, Math.floor((window.innerHeight - 250) / 60));
    setPageSize(rows);
    setIsWide(window.innerWidth >= 1024);
    setIsTiny(window.innerWidth < 900);
  };
  useEffect(() => { calc(); window.addEventListener('resize', calc); return () => window.removeEventListener('resize', calc); }, []);
  useEffect(() => setPage(0), [reservations.length, pageSize]);

  /* initial fetch */
  useEffect(() => {
    (async () => {
      setLoading(true); setErr('');
      try {
        const [resRes, slotRes, locRes] = await Promise.all([
          api.get('/reservation/reservations'),
          api.get('/parking_slot/slots'),
          api.get('/parking_location/locations'),
        ]);
        const base = resRes.reservations;
        const list = me.role === 'admin' && asUser ? base.filter(r => Number(r.user_id) === myId) : base;
        setReservations(list);
        setSlotMap(Object.fromEntries(slotRes.slots.map(s => [Number(s.id), s])));
        setLocMap (Object.fromEntries(locRes.locations.map(l => [Number(l.id), l])));

        if (me.role === 'admin') {
          mergeUsers((await api.get('/users/')).users);
        } else if (!me.first_name || !me.last_name) {
          const { user } = await api.get('/users/me');
          mergeUsers([user]);
        } else mergeUsers();
      } catch (e) { setErr(e.message); }
      finally     { setLoading(false); }
    })();
  }, [asUser]);

  /* lazy‑load missing users (admin) */
  useEffect(() => {
    if (me.role !== 'admin') return;
    const unknown = [...new Set(reservations.map(r => Number(r.user_id)))].filter(id => !(id in userMap));
    if (!unknown.length) return;
    (async () => {
      try {
        const fetched = await Promise.all(unknown.map(id => api.get(`/users/${id}`).then(r => r.user).catch(() => null)));
        mergeUsers(fetched.filter(Boolean));
      } catch {/* ignore */ }
    })();
  }, [reservations, userMap]);

  /* actions */
  const actOn = async r => {
    const ep = r.status.endsWith('booked') ? 'cancel' : r.status.endsWith('ongoing') ? 'finish' : null;
    if (!ep) return;
    try {
      await api.post(`/reservation/reservations/${r.id}/${ep}`);
      notify(ep === 'cancel' ? 'Reservation cancelled' : 'Reservation marked finished');
      const { reservations: refreshed } = await api.get('/reservation/reservations');
      setReservations(refreshed);
    } catch (e) { toast.error(e.message); }
  };

  /* helpers */
  const btn = (r, plain) => (
    <button
      onClick={() => actOn(r)}
      className={`rounded px-2 py-1 text-white text-xs font-medium shadow-sm
                 ${plain === 'booked'
                   ? 'bg-red-600 hover:bg-red-700'
                   : 'bg-green-600 hover:bg-green-700'}`}
    >
      {plain === 'booked'
        ? (isTiny ? '🗑️' : '🗑️ Cancel')
        : (isTiny ? '✔️' : '✔️ Finish')}
    </button>
  );

  const chip = stat => {
    const k = stat.split('.').pop();
    const cls = {
      booked   :'bg-yellow-100 text-yellow-800',
      ongoing  :'bg-green-100  text-green-800',
      finished :'bg-gray-100   text-gray-800',
      cancelled:'bg-red-100    text-red-800',
    }[k] || 'bg-gray-100 text-gray-800';
    return <span className={`px-2 py-0.5 rounded text-xs font-semibold ${cls}`}>{k}</span>;
  };

  const slotLabel = r => {
    const slot = slotMap[Number(r.slot_id)] || {}; const loc = locMap[Number(slot.location_id)] || {};
    return `${loc.name ?? '—'} • ${slot.slot_label ?? r.slot_id}`;
  };

  const allRows = useMemo(() => {
    const base = filter === 'all' ? reservations : reservations.filter(r => r.status.endsWith(filter));
    return [...base].sort((a,b) => new Date(b.start_ts) - new Date(a.start_ts));
  }, [reservations, filter]);

  const pagedRows  = isWide ? allRows.slice(page * pageSize, page * pageSize + pageSize) : allRows;
  const totalPages = isWide ? Math.ceil(allRows.length / pageSize) : 1;

  /* ───────── render ───────── */
  if (loading) return <p className="p-6 text-sm text-indigo-100">Loading…</p>;
  if (err)     return <p className="p-6 text-sm text-red-300">{err}</p>;

  return (
    <main className="relative min-h-screen flex flex-col items-center bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 text-white overflow-hidden p-6">
      {/* grain / blobs – omitted for brevity */}

      <section className="relative z-10 w-full max-w-6xl mt-6 h-[85vh] p-8 flex flex-col backdrop-blur-md bg-white/10 border border-white/20 rounded-3xl shadow-2xl">
        {/* header */}
        <header className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <h1 className="text-2xl sm:text-4xl font-extrabold drop-shadow-lg">My Reservations</h1>
          <select value={filter} onChange={e=>setFilter(e.target.value)}
                  className="rounded-lg border border-white/20 bg-white/90 text-blue-700 px-3 py-1.5 text-sm shadow-sm focus:ring focus:ring-blue-200">
            {['all','booked','ongoing','finished','cancelled'].map(o => <option key={o}>{o}</option>) }
          </select>
        </header>

        {/* list */}
        {isTiny ? (
          /* card layout */
          <ul className="mt-6 flex-1 overflow-y-auto pr-1 space-y-3 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
            {allRows.map(r => {
              const p = r.status.split('.').pop(); const doAct = ['booked','ongoing'].includes(p);
              return (
                <li key={r.id} className="bg-white/85 rounded-2xl p-4 text-blue-900 shadow flex flex-col gap-1">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold truncate max-w-[60%]">{slotLabel(r)}</span>
                    {chip(r.status)}
                  </div>
                  <p className="text-[11px] leading-tight">
                    {new Date(r.start_ts).toLocaleString('en-PH',{timeZone:'Asia/Manila'})} →<br/>
                    {new Date(r.end_ts).toLocaleString('en-PH',{timeZone:'Asia/Manila'})}
                  </p>
                  <p className="text-[11px] text-blue-700/80 truncate">{userMap[Number(r.user_id)] ?? r.user_id}</p>
                  {doAct && <div className="mt-2 self-end">{btn(r,p)}</div>}
                </li>
              );})}
            {!allRows.length && <p className="text-center text-sm text-indigo-800 mt-8">No reservations match this filter.</p>}
          </ul>
        ) : (
          /* table layout */
          <div className="mt-6 flex-1 overflow-y-auto rounded-lg bg-white/60 pr-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
            <table className="w-full table-fixed text-[12px] text-blue-900">
              <thead className="bg-white/70 text-xs font-semibold uppercase tracking-wide text-blue-800 border-b border-white/60">
                <tr>
                  <th className="px-1 py-3 text-left w-[17%]">Name</th>
                  <th className="px-1 py-3 text-left w-[21%]">Slot</th>
                  <th className="px-1 py-3 text-left w-[17%]">Start</th>
                  <th className="px-1 py-3 text-left w-[17%]">End</th>
                  <th className="px-1 py-3 text-left w-[12%]">Status</th>
                  <th className="px-1 py-3 text-right w-[8%]"></th>
                </tr>
              </thead>
              <tbody>
                {pagedRows.map(r => {
                  const p = r.status.split('.').pop(); const doAct = ['booked','ongoing'].includes(p);
                  return (
                    <tr key={r.id} className="border-b border-white/40 odd:bg-white/20 even:bg-white/40 hover:bg-white/60">
                      <td className="px-1 py-3 whitespace-nowrap truncate">{userMap[Number(r.user_id)] ?? r.user_id}</td>
                      <td className="px-1 py-3 whitespace-nowrap truncate">{slotLabel(r)}</td>
                      <td className="px-1 py-3 whitespace-nowrap">{new Date(r.start_ts).toLocaleString('en-PH',{timeZone:'Asia/Manila'})}</td>
                      <td className="px-1 py-3 whitespace-nowrap">{new Date(r.end_ts).toLocaleString('en-PH',{timeZone:'Asia/Manila'})}</td>
                      <td className="px-1 py-3">{chip(r.status)}</td>
                      <td className="px-1 py-3 text-right">{doAct && btn(r,p)}</td>
                    </tr>
                  );})}
                {!pagedRows.length && <tr><td colSpan={6} className="px-1 py-6 text-center text-indigo-800">No reservations match this filter.</td></tr>}
              </tbody>
            </table>
          </div>
        )}

        {/* pagination */}
        {isWide && totalPages>1 && (
          <div className="mt-4 flex justify-center items-center gap-4 text-sm">
            <button onClick={()=>setPage(p=>Math.max(0,p-1))}
                    disabled={page===0}
                    className="px-3 py-1 rounded-lg border border-white/30 hover:bg-white/20 disabled:opacity-40 disabled:cursor-not-allowed">⬅ Prev</button>
            <span>Page {page+1} / {totalPages}</span>
            <button onClick={()=>setPage(p=>Math.min(totalPages-1,p+1))}
                    disabled={page===totalPages-1}
                    className="px-3 py-1 rounded-lg border border-white/30 hover:bg-white/20 disabled:opacity-40 disabled:cursor-not-allowed">Next ➡</button>
          </div>
        )}
      </section>
    </main>
  );
}
