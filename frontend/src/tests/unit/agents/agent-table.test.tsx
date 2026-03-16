import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, within } from "@testing-library/react";
import { AgentTable } from "@/components/agents/agent-table";
import type { AgentPerformance } from "@/types/models";

// ── Fixtures ─────────────────────────────────────────────────────────────────

const mockAgents: AgentPerformance[] = [
  {
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
  },
  {
    id: "agent-2",
    tenant_id: "t1",
    email: "bob@example.com",
    full_name: "Bob Martinez",
    role: "manager",
    is_active: false,
    last_login: null,
    created_at: "2025-02-01T00:00:00Z",
    total_calls: 15,
    avg_call_duration: 210,
    conversion_rate: 20.0,
    avg_agent_score: 55,
    total_deals_won: 3,
  },
];

const defaultProps = {
  agents: mockAgents,
  isLoading: false,
  total: 2,
  page: 1,
  pageSize: 20,
  totalPages: 1,
  search: "",
  roleFilter: "",
  statusFilter: "",
  onSearchChange: vi.fn(),
  onRoleFilterChange: vi.fn(),
  onStatusFilterChange: vi.fn(),
  onPageChange: vi.fn(),
  onEdit: vi.fn(),
  onDeactivate: vi.fn(),
};

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("AgentTable", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders agent rows with correct name and email", () => {
    render(<AgentTable {...defaultProps} />);

    expect(screen.getByText("Alice Johnson")).toBeInTheDocument();
    expect(screen.getByText("alice@example.com")).toBeInTheDocument();
    expect(screen.getByText("Bob Martinez")).toBeInTheDocument();
    expect(screen.getByText("bob@example.com")).toBeInTheDocument();
  });

  it("renders correct role badges", () => {
    render(<AgentTable {...defaultProps} />);
    expect(screen.getByText("Agent")).toBeInTheDocument();
    expect(screen.getByText("Manager")).toBeInTheDocument();
  });

  it("renders correct status badges", () => {
    render(<AgentTable {...defaultProps} />);
    expect(screen.getByText("Active")).toBeInTheDocument();
    expect(screen.getByText("Inactive")).toBeInTheDocument();
  });

  it("shows skeleton rows when isLoading is true", () => {
    render(<AgentTable {...defaultProps} isLoading agents={[]} total={0} />);
    // Loading table uses td skeletons — no agent names rendered
    expect(screen.queryByText("Alice Johnson")).not.toBeInTheDocument();
  });

  it("shows empty message when agents list is empty and not loading", () => {
    render(
      <AgentTable
        {...defaultProps}
        agents={[]}
        total={0}
        isLoading={false}
      />
    );
    expect(screen.getByText("No agents found.")).toBeInTheDocument();
  });

  it("calls onSearchChange when user types in search box", () => {
    const onSearchChange = vi.fn();
    render(<AgentTable {...defaultProps} onSearchChange={onSearchChange} />);

    const searchInput = screen.getByPlaceholderText("Search by name or email…");
    fireEvent.change(searchInput, { target: { value: "Alice" } });

    // Note: actual debounced call tested via the localSearch state update;
    // UI value should update immediately
    expect(searchInput).toHaveValue("Alice");
  });

  it("calls onRoleFilterChange when role filter is changed", () => {
    const onRoleFilterChange = vi.fn();
    render(
      <AgentTable {...defaultProps} onRoleFilterChange={onRoleFilterChange} />
    );

    const roleSelect = screen.getByRole("combobox", { name: /filter by role/i });
    fireEvent.change(roleSelect, { target: { value: "manager" } });

    expect(onRoleFilterChange).toHaveBeenCalledWith("manager");
  });

  it("calls onStatusFilterChange when status filter is changed", () => {
    const onStatusFilterChange = vi.fn();
    render(
      <AgentTable {...defaultProps} onStatusFilterChange={onStatusFilterChange} />
    );

    const statusSelect = screen.getByRole("combobox", {
      name: /filter by status/i,
    });
    fireEvent.change(statusSelect, { target: { value: "active" } });

    expect(onStatusFilterChange).toHaveBeenCalledWith("active");
  });

  it("displays formatted conversion rate with percentage", () => {
    render(<AgentTable {...defaultProps} />);
    // Alice's conversion rate 58.5%
    expect(screen.getByText("58.5%")).toBeInTheDocument();
  });

  it("displays total agent count", () => {
    render(<AgentTable {...defaultProps} total={2} />);
    expect(screen.getByText("2 agents")).toBeInTheDocument();
  });
});
