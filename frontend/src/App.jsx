import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login       from './pages/Login';
import Dashboard   from './pages/Dashboard';
import Home        from './pages/Home';
import Layout      from './components/Layout';
import Protected   from './components/ProtectedRoute';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* public */}
        <Route path="/login" element={<Login />} />

        {/* everything below uses the shared Layout */}
        <Route element={<Layout />}>
          <Route
            path="/"
            element={
              <Protected>
                <Home />            {/* simple landing page for users */}
              </Protected>
            }
          />

          <Route
            path="/dashboard"
            element={
              <Protected>
                <Dashboard />       {/* admin & user dashboard */}
              </Protected>
            }
          />
        </Route>

        {/* 404 fallback (optional) */}
        <Route path="*" element={<p className="p-6">404 Page not found</p>} />
      </Routes>
    </BrowserRouter>
  );
}
