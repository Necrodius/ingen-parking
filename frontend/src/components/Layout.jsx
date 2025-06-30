import { Outlet } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Nav from './Nav';

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      <Nav />

      {/* Global toast notifications */}
      <Toaster
        position="top-center"
        toastOptions={{
          className: 'text-sm font-medium',
          duration: 4000,
        }}
      />

      {/* Main content */}
      <main className="flex-1 p-6">
        <div className="max-w-4xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
