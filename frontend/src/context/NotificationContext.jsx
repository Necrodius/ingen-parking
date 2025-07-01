import { createContext, useContext, useState, useCallback } from 'react';
import { toast } from 'react-hot-toast';

const NotificationContext = createContext();

export const useNotifications = () => useContext(NotificationContext);

export function NotificationProvider({ children }) {
  const [list, setList] = useState([]);          // { id, msg, ts, read }

  const notify = useCallback((msg) => {
    const id  = Date.now();
    setList((prev) => [{ id, msg, ts: new Date(), read: false }, ...prev].slice(0, 50));
    toast.success(msg);
  }, []);

  const markAllRead = () =>
    setList((prev) => prev.map((n) => ({ ...n, read: true })));

  return (
    <NotificationContext.Provider value={{ list, notify, markAllRead }}>
      {children}
    </NotificationContext.Provider>
  );
}
