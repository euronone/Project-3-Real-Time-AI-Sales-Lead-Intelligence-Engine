"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { cn } from "@/lib/utils";

interface DropdownItem {
  label: string;
  icon?: ReactNode;
  onClick: () => void;
  isDanger?: boolean;
  divider?: boolean;
  disabled?: boolean;
}

interface DropdownProps {
  trigger: ReactNode;
  items: DropdownItem[];
  align?: "left" | "right";
  className?: string;
}

export function Dropdown({ trigger, items, align = "right", className }: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const triggerRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const [focusedIndex, setFocusedIndex] = useState(-1);

  useEffect(() => {
    if (!isOpen) {
      setFocusedIndex(-1);
      return;
    }
    if (triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect();
      setPosition({
        top: rect.bottom + window.scrollY + 4,
        left:
          align === "right"
            ? rect.right + window.scrollX
            : rect.left + window.scrollX,
      });
    }
  }, [isOpen, align]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        !triggerRef.current?.contains(e.target as Node) &&
        !menuRef.current?.contains(e.target as Node)
      ) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    const activeItems = items.filter((item) => !item.divider && !item.disabled);
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setFocusedIndex((prev) => Math.min(prev + 1, activeItems.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setFocusedIndex((prev) => Math.max(prev - 1, 0));
    } else if (e.key === "Enter" && focusedIndex >= 0) {
      activeItems[focusedIndex]?.onClick();
      setIsOpen(false);
    } else if (e.key === "Escape") {
      setIsOpen(false);
    }
  };

  return (
    <div ref={triggerRef} className={cn("relative inline-block", className)}>
      <div onClick={() => setIsOpen((prev) => !prev)} onKeyDown={handleKeyDown}>
        {trigger}
      </div>

      {isOpen &&
        createPortal(
          <div
            ref={menuRef}
            style={{
              position: "absolute",
              top: position.top,
              ...(align === "right"
                ? { right: `calc(100vw - ${position.left}px)` }
                : { left: position.left }),
            }}
            className="z-50 min-w-[160px] bg-white border border-gray-200 rounded-lg shadow-lg py-1 animate-fade-in"
            role="menu"
          >
            {items.map((item, index) => {
              if (item.divider) {
                return <div key={index} className="my-1 border-t border-gray-100" />;
              }
              return (
                <button
                  key={index}
                  role="menuitem"
                  disabled={item.disabled}
                  onClick={() => {
                    item.onClick();
                    setIsOpen(false);
                  }}
                  className={cn(
                    "w-full flex items-center gap-2.5 px-4 py-2 text-sm text-left transition-colors",
                    item.isDanger
                      ? "text-red-600 hover:bg-red-50"
                      : "text-gray-700 hover:bg-gray-50",
                    item.disabled && "opacity-50 cursor-not-allowed pointer-events-none"
                  )}
                >
                  {item.icon && <span className="flex-shrink-0">{item.icon}</span>}
                  {item.label}
                </button>
              );
            })}
          </div>,
          document.body
        )}
    </div>
  );
}
