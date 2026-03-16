import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { AgentScorecard } from "@/components/agents/agent-scorecard";
import type { AgentScorecard as AgentScorecardType } from "@/types/models";

// ── Mock recharts to avoid jsdom SVG rendering issues ────────────────────────
vi.mock("recharts", () => ({
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
        <div data-testid="recharts-container">{children}</div>
    ),
    AreaChart: ({ children }: { children: React.ReactNode }) => (
        <div data-testid="area-chart">{children}</div>
    ),
    LineChart: ({ children }: { children: React.ReactNode }) => (
        <div data-testid="line-chart">{children}</div>
    ),
    Area: () => null,
    Line: () => null,
    XAxis: () => null,
    YAxis: () => null,
    CartesianGrid: () => null,
    Tooltip: () => null,
    defs: () => null,
    linearGradient: () => null,
    stop: () => null,
}));

// ── Fixture ──────────────────────────────────────────────────────────────────

const mockScorecard: AgentScorecardType = {
    agent_id: "agent-1",
    period_days: 30,
    total_calls: 42,
    avg_call_duration: 180,
    conversion_rate: 58.5,
    avg_agent_score: 82,
    total_deals_won: 24,
    top_objections: ["Price too high", "Need to think about it", "Not the right time"],
    call_trend: [
        { date: "2026-03-01", count: 5 },
        { date: "2026-03-02", count: 8 },
    ],
    score_trend: [
        { date: "2026-03-01", score: 78 },
        { date: "2026-03-02", score: 82 },
    ],
};

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("AgentScorecard", () => {
    it("renders skeleton when isLoading is true", () => {
        const { container } = render(
            <AgentScorecard isLoading />
        );
        // Skeleton elements should be present (animated divs)
        expect(container.firstChild).toBeTruthy();
    });

    it("renders empty state when no scorecard data", () => {
        render(<AgentScorecard />);
        expect(screen.getByText("No scorecard data available yet.")).toBeInTheDocument();
    });

    it("renders total calls KPI card", () => {
        render(<AgentScorecard scorecard={mockScorecard} />);
        expect(screen.getByText("Total Calls")).toBeInTheDocument();
        expect(screen.getByText("42")).toBeInTheDocument();
        expect(screen.getByText("Last 30 days")).toBeInTheDocument();
    });

    it("renders conversion rate KPI", () => {
        render(<AgentScorecard scorecard={mockScorecard} />);
        expect(screen.getByText("Conversion Rate")).toBeInTheDocument();
        expect(screen.getByText("58.5%")).toBeInTheDocument();
    });

    it("renders avg agent score KPI", () => {
        render(<AgentScorecard scorecard={mockScorecard} />);
        expect(screen.getByText("Avg Score")).toBeInTheDocument();
        expect(screen.getByText("82")).toBeInTheDocument();
        expect(screen.getByText("out of 100")).toBeInTheDocument();
    });

    it("renders total deals won KPI", () => {
        render(<AgentScorecard scorecard={mockScorecard} />);
        expect(screen.getByText("Deals Won")).toBeInTheDocument();
        expect(screen.getByText("24")).toBeInTheDocument();
    });

    it("renders top objections as badges", () => {
        render(<AgentScorecard scorecard={mockScorecard} />);
        expect(screen.getByText("Top Objections Handled")).toBeInTheDocument();
        expect(screen.getByText("Price too high")).toBeInTheDocument();
        expect(screen.getByText("Need to think about it")).toBeInTheDocument();
        expect(screen.getByText("Not the right time")).toBeInTheDocument();
    });

    it("does not render top objections section when list is empty", () => {
        const scorecard = { ...mockScorecard, top_objections: [] };
        render(<AgentScorecard scorecard={scorecard} />);
        expect(screen.queryByText("Top Objections Handled")).not.toBeInTheDocument();
    });

    it("renders chart containers", () => {
        render(<AgentScorecard scorecard={mockScorecard} />);
        expect(screen.getByText("Call Volume (last 30 days)")).toBeInTheDocument();
        expect(screen.getByText("AI Score Trend (last 30 days)")).toBeInTheDocument();
    });

    it("shows formatted avg call duration", () => {
        render(<AgentScorecard scorecard={mockScorecard} />);
        // 180 seconds = 3m
        expect(screen.getByText("3m")).toBeInTheDocument();
    });
});
