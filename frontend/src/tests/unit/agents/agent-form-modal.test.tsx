import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AgentFormModal } from "@/components/agents/agent-form-modal";
import type { AgentPerformance } from "@/types/models";

// ── Fixtures ─────────────────────────────────────────────────────────────────

const mockAgent: AgentPerformance = {
  id: "agent-1",
  tenant_id: "t1",
  email: "alice@example.com",
  full_name: "Alice Johnson",
  role: "agent",
  is_active: true,
  last_login: "2026-03-10T10:00:00Z",
  created_at: "2025-01-01T00:00:00Z",
  total_calls: 42,
  avg_call_duration: 180,
  conversion_rate: 58.5,
  avg_agent_score: 82,
  total_deals_won: 24,
};

// createPortal requires a DOM body node; polyfill in jsdom
vi.mock("react-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-dom")>();
  return {
    ...actual,
    createPortal: (children: React.ReactNode) => children,
  };
});

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("AgentFormModal — Create mode", () => {
  const onSubmit = vi.fn();
  const onClose = vi.fn();

  const renderModal = () =>
    render(
      <AgentFormModal
        isOpen
        onClose={onClose}
        agent={null}
        onSubmit={onSubmit}
      />
    );

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders modal title 'Create Agent'", () => {
    renderModal();
    expect(screen.getByText("Create Agent")).toBeInTheDocument();
  });

  it("renders empty name and email fields", () => {
    renderModal();
    const nameInput = screen.getByLabelText(/full name/i);
    const emailInput = screen.getByLabelText(/email address/i);
    expect(nameInput).toHaveValue("");
    expect(emailInput).toHaveValue("");
  });

  it("shows validation errors when submitting empty form", async () => {
    renderModal();
    fireEvent.click(screen.getByText("Create Agent", { selector: "button" }));

    await waitFor(() => {
      expect(
        screen.getByText("Full name must be at least 2 characters")
      ).toBeInTheDocument();
      expect(
        screen.getByText("Email is required")
      ).toBeInTheDocument();
    });
  });

  it("shows email validation error for invalid email", async () => {
    renderModal();
    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/full name/i), "Jane Doe");
    await user.type(screen.getByLabelText(/email address/i), "not-an-email");
    fireEvent.click(screen.getByText("Create Agent", { selector: "button" }));

    await waitFor(() => {
      expect(
        screen.getByText("Please enter a valid email address")
      ).toBeInTheDocument();
    });
  });

  it("calls onSubmit with correct payload when form is valid", async () => {
    renderModal();
    const user = userEvent.setup();

    await user.type(screen.getByLabelText(/full name/i), "Jane Doe");
    await user.type(screen.getByLabelText(/email address/i), "jane@example.com");

    fireEvent.click(screen.getByText("Create Agent", { selector: "button" }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          full_name: "Jane Doe",
          email: "jane@example.com",
          role: "agent",
        })
      );
    });
  });

  it("calls onClose when Cancel is clicked", () => {
    renderModal();
    fireEvent.click(screen.getByText("Cancel"));
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});

describe("AgentFormModal — Edit mode", () => {
  const onSubmit = vi.fn();
  const onClose = vi.fn();

  const renderEditModal = () =>
    render(
      <AgentFormModal
        isOpen
        onClose={onClose}
        agent={mockAgent}
        onSubmit={onSubmit}
      />
    );

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders modal title 'Edit Agent'", () => {
    renderEditModal();
    expect(screen.getByText("Edit Agent")).toBeInTheDocument();
  });

  it("pre-fills name field with agent's full name", () => {
    renderEditModal();
    const nameInput = screen.getByLabelText(/full name/i);
    expect(nameInput).toHaveValue("Alice Johnson");
  });

  it("disables email field in edit mode", () => {
    renderEditModal();
    const emailInput = screen.getByLabelText(/email address/i);
    expect(emailInput).toBeDisabled();
  });

  it("calls onSubmit with updated name when form saved", async () => {
    renderEditModal();
    const user = userEvent.setup();

    const nameInput = screen.getByLabelText(/full name/i);
    await user.clear(nameInput);
    await user.type(nameInput, "Alice Smith");

    fireEvent.click(screen.getByText("Save Changes"));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({ full_name: "Alice Smith" })
      );
    });
  });
});
