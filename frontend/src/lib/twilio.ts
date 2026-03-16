// Twilio Client JS SDK wrapper
// Actual Twilio Device is initialized lazily when an agent starts a call

// NOTE: twilio-client must be imported client-side only
// Use dynamic import in hooks/use-call.ts to avoid SSR issues

let deviceInstance: unknown = null;

export async function initTwilioDevice(token: string): Promise<unknown> {
  // Dynamic import to prevent SSR crashes
  const { Device } = await import("twilio-client");

  if (deviceInstance) {
    destroyTwilioDevice();
  }

  const device = new Device(token, {
    codecPreferences: ["opus", "pcmu"],
    fakeLocalDTMF: true,
    enableRingingState: true,
  });

  device.on("ready", () => {
    console.info("[Twilio] Device ready");
  });

  device.on("error", (error: { message: string }) => {
    console.error("[Twilio] Device error:", error.message);
  });

  device.on("disconnect", () => {
    console.info("[Twilio] Call disconnected");
  });

  deviceInstance = device;
  return device;
}

export function destroyTwilioDevice(): void {
  if (deviceInstance) {
    (deviceInstance as { destroy: () => void }).destroy();
    deviceInstance = null;
  }
}

export function getTwilioDevice(): unknown {
  return deviceInstance;
}
