import React, { createContext, useContext, useState, useCallback } from "react";

const NotificationContext = createContext(null);

let _nextId = 1;

// Notification types: "incident" | "report" | "alert" | "ack"
const TYPE_META = {
  incident: { icon: "warning", label: "Incident Created" },
  report:   { icon: "description", label: "Report Generated" },
  alert:    { icon: "notifications_active", label: "High Risk Alert" },
  ack:      { icon: "check_circle", label: "Alert Acknowledged" },
};

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);

  const addNotification = useCallback(({ type = "incident", title, message }) => {
    const meta = TYPE_META[type] || TYPE_META.incident;
    const notif = {
      id: _nextId++,
      type,
      icon: meta.icon,
      label: meta.label,
      title: title || meta.label,
      message: message || "",
      read: false,
      timestamp: new Date().toISOString(),
    };
    setNotifications(prev => [notif, ...prev].slice(0, 50)); // keep max 50
  }, []);

  const markRead = useCallback((id) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  }, []);

  const markAllRead = useCallback(() => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <NotificationContext.Provider value={{
      notifications,
      unreadCount,
      addNotification,
      markRead,
      markAllRead,
      clearAll,
    }}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotifications() {
  const ctx = useContext(NotificationContext);
  if (!ctx) throw new Error("useNotifications must be used within NotificationProvider");
  return ctx;
}

