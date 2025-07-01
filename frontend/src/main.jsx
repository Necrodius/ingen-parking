import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';
import { AuthProvider } from './context/AuthContext';
import { NotificationProvider } from './context/NotificationContext';
import { Toaster } from 'react-hot-toast';
import 'leaflet/dist/leaflet.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <NotificationProvider>
        <App />
        {/* global toast pop‑ups */}
        <Toaster
          position="top-center"
          toastOptions={{ className: 'text-sm font-medium', duration: 4000 }}
        />
      </NotificationProvider>
    </AuthProvider>
  </React.StrictMode>
);
