import { Outlet } from 'react-router-dom';
import Nav from './Nav';

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      <Nav />

      {/* main page content */}
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  );
}
