import { Outlet, useLocation } from 'react-router-dom';  // `useLocation` provides access to the current URL path
import { Toaster } from 'react-hot-toast';               // Toast notification system
import Nav from './Nav';                                 // Shared navigation bar across all pages

/* Wraps all pages with common UI elements */
export default function Layout() {
  const { pathname } = useLocation(); // Destructure current URL path
  const isHome = pathname === '/';    // Determine if the current page is the Home page

  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      {/* Global navigation bar visible on all pages */}
      <Nav />

      {/* Toast notifications rendered at the top-center of the screen */}
      <Toaster
        position="top-center"
        toastOptions={{
          className: 'text-sm font-medium',
          duration: 4000,
        }}
      />

      {/* Main content container */}
      <main className="flex-1 p-6">
        {isHome ? (
          // If on the home page, render the route content as full width
          <Outlet />
        ) : (
          // For all other routes, center the content and limit max width
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        )}
      </main>
    </div>
  );
}
