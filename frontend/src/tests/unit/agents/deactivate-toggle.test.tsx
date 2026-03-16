import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { DeactivateToggle } from "@/components/agents/deactivate-toggle";

// createPortal polyfill for jsdom
vi.mock("react-dom", async (importOriginal) => {
    const actual = await importOriginal<typeof import("react-dom")>();
    return {
        ...actual,
        createPortal: (children: React.ReactNode) => children,
    };
});

describe("DeactivateToggle — active agent", () => {
    const onConfirm = vi.fn();

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it("renders as checked (green) when agent is active", () => {
        render(
            <DeactivateToggle
                isActive
                agentName="Alice Johnson"
                onConfirm={onConfirm}
            />
        );
        const switchEl = screen.getByRole("switch", { name: /deactivate agent/i });
        expect(switchEl).toHaveAttribute("aria-checked", "true");
    });

    it("opens confirmation modal on click when active", () => {
        render(
            <DeactivateToggle
                isActive
                agentName="Alice Johnson"
                onConfirm={onConfirm}
            />
        );

        const switchEl = screen.getByRole("switch", { name: /deactivate agent/i });
        fireEvent.click(switchEl);

        expect(screen.getByText("Deactivate Agent")).toBeInTheDocument();
        expect(screen.getByText(/Are you sure you want to deactivate/i)).toBeInTheDocument();
        expect(screen.getByText("Alice Johnson")).toBeInTheDocument();
    });

    it("calls onConfirm when Deactivate button in modal is clicked", () => {
        render(
            <DeactivateToggle
                isActive
                agentName="Alice Johnson"
                onConfirm={onConfirm}
            />
        );

        fireEvent.click(screen.getByRole("switch"));
        fireEvent.click(screen.getByRole("button", { name: "Deactivate" }));

        expect(onConfirm).toHaveBeenCalledTimes(1);
    });

    it("dismisses modal when Cancel is clicked", () => {
        render(
            <DeactivateToggle
                isActive
                agentName="Alice Johnson"
                onConfirm={onConfirm}
            />
        );

        fireEvent.click(screen.getByRole("switch"));
        expect(screen.getByText("Deactivate Agent")).toBeInTheDocument();

        fireEvent.click(screen.getByText("Cancel"));
        expect(screen.queryByText("Deactivate Agent")).not.toBeInTheDocument();
        expect(onConfirm).not.toHaveBeenCalled();
    });
});

describe("DeactivateToggle — inactive agent", () => {
    const onConfirm = vi.fn();

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it("renders as unchecked when agent is inactive", () => {
        render(
            <DeactivateToggle
                isActive={false}
                agentName="Bob Martinez"
                onConfirm={onConfirm}
            />
        );
        const switchEl = screen.getByRole("switch", { name: /activate agent/i });
        expect(switchEl).toHaveAttribute("aria-checked", "false");
    });

    it("calls onConfirm immediately without modal when inactive", () => {
        render(
            <DeactivateToggle
                isActive={false}
                agentName="Bob Martinez"
                onConfirm={onConfirm}
            />
        );
        const switchEl = screen.getByRole("switch", { name: /activate agent/i });
        fireEvent.click(switchEl);

        // No modal should appear
        expect(screen.queryByText("Deactivate Agent")).not.toBeInTheDocument();
        expect(onConfirm).toHaveBeenCalledTimes(1);
    });
});

describe("DeactivateToggle — loading state", () => {
    it("disables the switch when isPending is true", () => {
        render(
            <DeactivateToggle
                isActive
                agentName="Alice Johnson"
                isPending
                onConfirm={vi.fn()}
            />
        );
        const switchEl = screen.getByRole("switch");
        expect(switchEl).toBeDisabled();
    });
});
