"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { createPortal } from "react-dom";
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from "lucide-react";
import { cn } from "@/lib/utils";

type ToastVariant = "success" | "error" | "warning" | "info";

interface Toast {
  id: string;
  variant: ToastVariant;
  message: string;
}

interface ToastContextValue {
  toast: {
    success: (message: string) => void;
    error: (message: string) => void;
    warning: (message: string) => void;
    info: (message: string) => void;
  };
}

const ToastContext = createContext<ToastContextValue | null>(null);

const variantConfig: Record<
  ToastVariant,
  { icon: ReactNode; classes: string }
> = {
  success: {
    icon: <CheckCircle size={18} />,
    classes: "bg-green-50 border-green-200 text-green-800",
  },
  error: {
    icon: <AlertCircle size={18} />,
    classes: "bg-red-50 border-red-200 text-red-800",
  },
  warning: {
    icon: <AlertTriangle size={18} />,
    classes: "bg-yellow-50 border-yellow-200 text-yellow-800",
  },
  info: {
    icon: <Info size={18} />,
    classes: "bg-blue-50 border-blue-200 text-blue-800",
  },
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  const addToast = useCallback((variant: ToastVariant, message: string) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev.slice(-4), { id, variant, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const toast = {
    success: (message: string) => addToast("success", message),
    error: (message: string) => addToast("error", message),
    warning: (message: string) => addToast("warning", message),
    info: (message: string) => addToast("info", message),
  };

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      {mounted &&
        createPortal(
          <div
            className="fixed top-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none"
            aria-live="polite"
          >
            {toasts.map((t) => {
              const config = variantConfig[t.variant];
              return (
                <div
                  key={t.id}
                  className={cn(
                    "flex items-start gap-3 px-4 py-3 rounded-lg border shadow-md",
                    "min-w-[300px] max-w-[420px] pointer-events-auto animate-slide-in",
                    config.classes
                  )}
                  role="alert"
                >
                  <span className="flex-shrink-0 mt-0.5">{config.icon}</span>
                  <p className="flex-1 text-sm font-medium">{t.message}</p>
                  <button
                    onClick={() => removeToast(t.id)}
                    className="flex-shrink-0 opacity-60 hover:opacity-100 transition-opacity"
                    aria-label="Dismiss notification"
                  >
                    <X size={16} />
                  </button>
                </div>
              );
            })}
          </div>,
          document.body
        )}
    </ToastContext.Provider>
  );
}

export function useToast(): ToastContextValue {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within ToastProvider");
  }
  return context;
}
