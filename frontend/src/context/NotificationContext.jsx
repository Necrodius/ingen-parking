import { createContext, useContext, useState, useCallback } from 'react';
import { toast } from 'react-hot-toast';

/* Create the context for managing in-app notifications */
const NotificationContext = createContext();

export const useNotifications = () => useContext(NotificationContext);

export function NotificationProvider({ children }) {
  /* Local state holds the notification list */
  const [list, setList] = useState([]);

  /* Adds a new notification to the top of the list and triggers a toast */
  const notify = useCallback((msg) => {
    const id = Date.now(); // use timestamp as a simple unique ID
    const newNotification = {
      id,
      msg,
      ts: new Date(),
      read: false,
    };

    /* Prepend the new notification and trim the list to the latest 50 */
    setList((prev) => [newNotification, ...prev].slice(0, 50));

    /* Trigger a toast notification using react-hot-toast */
    toast.success(msg);
  }, []);

  /* Marks all notifications in the list as read*/
  const markAllRead = () => {
    setList((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  return (
    <NotificationContext.Provider value={{ list, notify, markAllRead }}>
      {children}
    </NotificationContext.Provider>
  );
}
