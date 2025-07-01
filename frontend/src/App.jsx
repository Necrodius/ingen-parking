import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login           from './pages/Login';
import Dashboard       from './pages/Dashboard';
import Home            from './pages/Home';
import Layout          from './components/Layout';
import Protected       from './components/ProtectedRoute';
import Locations       from './pages/Locations';
import Slots           from './pages/Slots';
import MyReservations  from './pages/MyReservations';
import Profile         from './pages/Profile';
import AdminLocations  from './pages/AdminLocations';
import AdminUsers      from './pages/AdminUsers';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ---------- Public Routes ---------- */}
        <Route path="/login" element={<Login />} />

        {/* ---------- Protected Routes (shared <Layout>) ---------- */}
        <Route element={<Layout />}>
          {/* Home */}
          <Route
            path="/"
            element={
              <Protected>
                <Home />
              </Protected>
            }
          />

          {/* Admin dashboard */}
          <Route
            path="/dashboard"
            element={
              <Protected roles={['admin']}>
                <Dashboard />
              </Protected>
            }
          />

          {/* Admin: manage locations */}
          <Route
            path="/admin/locations"
            element={
              <Protected roles={['admin']}>
                <AdminLocations />
              </Protected>
            }
          />

          {/* Admin: manage users */}
          <Route
            path="/admin/users"
            element={
              <Protected roles={['admin']}>
                <AdminUsers />
              </Protected>
            }
          />

          {/* ---------- User booking flow ---------- */}
          <Route
            path="/locations"
            element={
              <Protected>
                <Locations />
              </Protected>
            }
          />
          <Route
            path="/locations/:id/slots"
            element={
              <Protected>
                <Slots />
              </Protected>
            }
          />
          <Route
            path="/my-reservations"
            element={
              <Protected>
                <MyReservations />
              </Protected>
            }
          />

          {/* ---------- User profile ---------- */}
          <Route
            path="/profile"
            element={
              <Protected>
                <Profile />
              </Protected>
            }
          />
        </Route>

        {/* ---------- Fallback (404) ---------- */}
        <Route path="*" element={<p className="p-6">404 Page not found</p>} />
      </Routes>
    </BrowserRouter>
  );
}
