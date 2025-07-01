import { createContext, useContext, useState, useCallback } from 'react';
import { toast } from 'react-hot-toast';

// Create the context for managing in-app notifications
const NotificationContext = createContext();

/**
 * useNotifications
 *
 * Custom hook to consume the notification context.
 * Gives access to the list of notifications and helper functions.
 */
export const useNotifications = () => useContext(NotificationContext);

/**
 * NotificationProvider
 *
 * Provides notification state and methods to components via context.
 * Features:
 * - Stores a list of recent in-app notifications (up to 50).
 * - Exposes a `notify` function to trigger a toast and store the message.
 * - Exposes a `markAllRead` function to mark all notifications as read.
 */
export function NotificationProvider({ children }) {
  // Local state holds the notification list: { id, msg, ts, read }
  const [list, setList] = useState([]);

  /**
   * notify
   *
   * Adds a new notification to the top of the list and triggers a toast.
   * Limits the list to 50 items to prevent memory bloat.
   */
  const notify = useCallback((msg) => {
    const id = Date.now(); // use timestamp as a simple unique ID
    const newNotification = {
      id,
      msg,
      ts: new Date(),
      read: false,
    };

    // Prepend the new notification and trim the list to the latest 50
    setList((prev) => [newNotification, ...prev].slice(0, 50));

    // Trigger a toast notification using react-hot-toast
    toast.success(msg);
  }, []);

  /**
   * markAllRead
   *
   * Marks all notifications in the list as "read"
   * (used to visually de-emphasize seen messages)
   */
  const markAllRead = () => {
    setList((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  return (
    <NotificationContext.Provider value={{ list, notify, markAllRead }}>
      {children}
    </NotificationContext.Provider>
  );
}
