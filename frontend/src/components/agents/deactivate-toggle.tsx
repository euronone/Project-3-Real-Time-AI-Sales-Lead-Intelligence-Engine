"use client";

import { useState } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

// ── Props ────────────────────────────────────────────────────────────────────

interface DeactivateToggleProps {
  isActive: boolean;
  agentName: string;
  isPending?: boolean;
  onConfirm: () => void;
}

// ── Component ────────────────────────────────────────────────────────────────

export function DeactivateToggle({
  isActive,
  agentName,
  isPending = false,
  onConfirm,
}: DeactivateToggleProps) {
  const [showConfirm, setShowConfirm] = useState(false);

  function handleToggleClick() {
    // Reactivating needs no confirmation — only deactivating does
    if (!isActive) {
      onConfirm();
      return;
    }
    setShowConfirm(true);
  }

  function handleConfirm() {
    setShowConfirm(false);
    onConfirm();
  }

  return (
    <>
      {/* ── Toggle switch ────────────────────────────────── */}
      <button
        type="button"
        role="switch"
        aria-checked={isActive}
        aria-label={isActive ? "Deactivate agent" : "Activate agent"}
        disabled={isPending}
        onClick={handleToggleClick}
        className={cn(
          "relative inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full",
          "border-2 border-transparent transition-colors duration-200 ease-in-out",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          isActive ? "bg-green-500" : "bg-gray-300"
        )}
      >
        <span
          className={cn(
            "pointer-events-none inline-block h-5 w-5 transform rounded-full",
            "bg-white shadow-md ring-0 transition duration-200 ease-in-out",
            isActive ? "translate-x-5" : "translate-x-0"
          )}
        />
      </button>

      {/* ── Confirmation modal ───────────────────────────── */}
      <Modal
        isOpen={showConfirm}
        onClose={() => setShowConfirm(false)}
        title="Deactivate Agent"
        size="sm"
        footer={
          <>
            <Button
              variant="outline"
              onClick={() => setShowConfirm(false)}
              disabled={isPending}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleConfirm}
              isLoading={isPending}
            >
              Deactivate
            </Button>
          </>
        }
      >
        <p className="text-sm text-gray-600">
          Are you sure you want to deactivate{" "}
          <span className="font-semibold text-gray-900">{agentName}</span>?
          They will lose access to the platform immediately.
        </p>
      </Modal>
    </>
  );
}
