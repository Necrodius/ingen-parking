// src/Layout.jsx
import { Outlet, useLocation } from 'react-router-dom';   // ⬅️  useLocation gives us pathname
import { Toaster } from 'react-hot-toast';
import Nav from './Nav';

export default function Layout() {
  const { pathname } = useLocation();
  const isHome = pathname === '/';          // tweak if your Home route has a different path

  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      <Nav />

      <Toaster
        position="top-center"
        toastOptions={{ className: 'text-sm font-medium', duration: 4000 }}
      />

      <main className="flex-1 p-6">
        {isHome ? (
          /* Home → no width cap */
          <Outlet />
        ) : (
          /* All other pages → centred 7xl cap */
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        )}
      </main>
    </div>
  );
}
