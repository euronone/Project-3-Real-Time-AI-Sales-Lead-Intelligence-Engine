import { create } from "zustand";
import type { ActiveCall, CallStatus } from "@/types/call";

interface CallState {
  activeCall: ActiveCall | null;
  callStatus: CallStatus | null;
  isMuted: boolean;
  isOnHold: boolean;
  twilioDevice: unknown | null;
  // Actions
  setActiveCall: (call: ActiveCall) => void;
  updateCallStatus: (status: CallStatus) => void;
  endCall: () => void;
  setMuted: (muted: boolean) => void;
  setOnHold: (onHold: boolean) => void;
  setTwilioDevice: (device: unknown) => void;
}

export const useCallStore = create<CallState>()((set) => ({
  activeCall: null,
  callStatus: null,
  isMuted: false,
  isOnHold: false,
  twilioDevice: null,

  setActiveCall: (call) =>
    set({ activeCall: call, callStatus: call.status, isMuted: false, isOnHold: false }),

  updateCallStatus: (status) =>
    set((state) => ({
      activeCall: state.activeCall ? { ...state.activeCall, status } : null,
      callStatus: status,
    })),

  endCall: () =>
    set({ activeCall: null, callStatus: null, isMuted: false, isOnHold: false }),

  setMuted: (isMuted) => set({ isMuted }),

  setOnHold: (isOnHold) => set({ isOnHold }),

  setTwilioDevice: (twilioDevice) => set({ twilioDevice }),
}));
