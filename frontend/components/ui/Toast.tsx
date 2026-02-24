'use client';

import { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastContextType {
  showToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

const toastConfig: Record<ToastType, { icon: ReactNode; bg: string; border: string; iconColor: string }> = {
  success: {
    icon: <CheckCircle className="h-5 w-5" />,
    bg: 'bg-green-50',
    border: 'border-l-green-400',
    iconColor: 'text-green-500',
  },
  error: {
    icon: <XCircle className="h-5 w-5" />,
    bg: 'bg-red-50',
    border: 'border-l-red-400',
    iconColor: 'text-red-500',
  },
  warning: {
    icon: <AlertTriangle className="h-5 w-5" />,
    bg: 'bg-yellow-50',
    border: 'border-l-yellow-400',
    iconColor: 'text-yellow-500',
  },
  info: {
    icon: <Info className="h-5 w-5" />,
    bg: 'bg-blue-50',
    border: 'border-l-blue-400',
    iconColor: 'text-blue-500',
  },
};

function ToastItem({ toast, onRemove }: { toast: Toast; onRemove: () => void }) {
  const config = toastConfig[toast.type];

  return (
    <div
      className={`flex items-start gap-3 rounded-lg border-l-4 p-4 shadow-lg ${config.bg} ${config.border} animate-slide-in`}
    >
      <div className={`shrink-0 ${config.iconColor}`}>{config.icon}</div>
      <p className="flex-1 text-sm font-medium text-gray-800">{toast.message}</p>
      <button
        onClick={onRemove}
        className="shrink-0 text-gray-400 transition-colors hover:text-gray-600"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((message: string, type: ToastType = 'info') => {
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { id, message, type }]);

    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {toasts.length > 0 && (
        <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
          {toasts.map((toast) => (
            <ToastItem key={toast.id} toast={toast} onRemove={() => removeToast(toast.id)} />
          ))}
        </div>
      )}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}
