import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login           from './pages/Login';
import Dashboard       from './pages/Dashboard';
import Home            from './pages/Home';
import Layout          from './components/Layout';
import Protected       from './components/ProtectedRoute';
import Locations       from './pages/Locations';
import Slots           from './pages/Slots';
import MyReservations  from './pages/MyReservations';
import Profile         from './pages/Profile'; // 🆕 Add this

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ---------- Public Routes ---------- */}
        <Route path="/login" element={<Login />} />

        {/* ---------- Protected Routes (with shared layout) ---------- */}
        <Route element={<Layout />}>
          <Route
            path="/"
            element={
              <Protected>
                <Home />
              </Protected>
            }
          />

          <Route
            path="/dashboard"
            element={
              <Protected>
                <Dashboard />
              </Protected>
            }
          />

          {/* ---------- User Booking Flow ---------- */}
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

          {/* ---------- User Profile ---------- */}
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
        <Route path="*" element={<p className="p-6">404 Page not found</p>} />
      </Routes>
    </BrowserRouter>
  );
}
