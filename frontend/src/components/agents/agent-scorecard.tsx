"use client";

import {
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { TrendingUp, Phone, Clock, Target, Star, Trophy } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/loading";
import { formatDuration } from "@/lib/utils";
import type { AgentScorecard } from "@/types/models";

// ── KPI Card ─────────────────────────────────────────────────────────────────

interface KpiCardProps {
  label: string;
  value: string;
  icon: React.ReactNode;
  subLabel?: string;
  color?: "blue" | "green" | "purple" | "yellow" | "orange";
}

const colorMap = {
  blue: { bg: "bg-blue-50", icon: "text-blue-600", value: "text-blue-700" },
  green: { bg: "bg-green-50", icon: "text-green-600", value: "text-green-700" },
  purple: { bg: "bg-purple-50", icon: "text-purple-600", value: "text-purple-700" },
  yellow: { bg: "bg-yellow-50", icon: "text-yellow-600", value: "text-yellow-700" },
  orange: { bg: "bg-orange-50", icon: "text-orange-600", value: "text-orange-700" },
};

function KpiCard({ label, value, icon, subLabel, color = "blue" }: KpiCardProps) {
  const c = colorMap[color];
  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
            {label}
          </p>
          <p className={`mt-1 text-2xl font-bold ${c.value}`}>{value}</p>
          {subLabel && (
            <p className="mt-0.5 text-xs text-gray-400">{subLabel}</p>
          )}
        </div>
        <div className={`p-2.5 rounded-xl ${c.bg}`}>
          <span className={c.icon}>{icon}</span>
        </div>
      </div>
    </Card>
  );
}

// ── Chart wrapper ─────────────────────────────────────────────────────────────

function ChartCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <Card className="p-5">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">{title}</h3>
      {children}
    </Card>
  );
}

// ── Skeleton ──────────────────────────────────────────────────────────────────

function ScorecardSkeleton() {
  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <Card key={i} className="p-4">
            <Skeleton className="h-3 w-20 mb-3" />
            <Skeleton className="h-7 w-14" />
          </Card>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card className="p-5 h-64">
          <Skeleton className="h-4 w-32 mb-4" />
          <Skeleton className="h-full w-full" />
        </Card>
        <Card className="p-5 h-64">
          <Skeleton className="h-4 w-32 mb-4" />
          <Skeleton className="h-full w-full" />
        </Card>
      </div>
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

interface AgentScorecardProps {
  scorecard?: AgentScorecard;
  isLoading?: boolean;
}

export function AgentScorecard({ scorecard, isLoading }: AgentScorecardProps) {
  if (isLoading) return <ScorecardSkeleton />;

  if (!scorecard) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-gray-400">
        <TrendingUp size={40} className="mb-3 opacity-40" />
        <p className="text-sm">No scorecard data available yet.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      {/* ── KPI row ──────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <KpiCard
          label="Total Calls"
          value={scorecard.total_calls.toString()}
          icon={<Phone size={18} />}
          subLabel={`Last ${scorecard.period_days} days`}
          color="blue"
        />
        <KpiCard
          label="Avg Duration"
          value={formatDuration(scorecard.avg_call_duration)}
          icon={<Clock size={18} />}
          color="purple"
        />
        <KpiCard
          label="Conversion Rate"
          value={`${scorecard.conversion_rate.toFixed(1)}%`}
          icon={<Target size={18} />}
          color={scorecard.conversion_rate >= 50 ? "green" : "yellow"}
        />
        <KpiCard
          label="Avg Score"
          value={scorecard.avg_agent_score.toFixed(0)}
          icon={<Star size={18} />}
          subLabel="out of 100"
          color={scorecard.avg_agent_score >= 80 ? "green" : "orange"}
        />
        <KpiCard
          label="Deals Won"
          value={scorecard.total_deals_won.toString()}
          icon={<Trophy size={18} />}
          color="green"
        />
      </div>

      {/* ── Charts row ───────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Call trend */}
        <ChartCard title="Call Volume (last 30 days)">
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart
              data={scorecard.call_trend}
              margin={{ top: 4, right: 8, left: -20, bottom: 0 }}
            >
              <defs>
                <linearGradient id="callGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 11 }}
                tickFormatter={(v: string) =>
                  new Date(v).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                  })
                }
              />
              <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
              <Tooltip
                labelFormatter={(v: string) =>
                  new Date(v).toLocaleDateString("en-US", {
                    weekday: "short",
                    month: "short",
                    day: "numeric",
                  })
                }
              />
              <Area
                type="monotone"
                dataKey="count"
                stroke="#3b82f6"
                strokeWidth={2}
                fill="url(#callGrad)"
                name="Calls"
              />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Score trend */}
        <ChartCard title="AI Score Trend (last 30 days)">
          <ResponsiveContainer width="100%" height={200}>
            <LineChart
              data={scorecard.score_trend}
              margin={{ top: 4, right: 8, left: -20, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 11 }}
                tickFormatter={(v: string) =>
                  new Date(v).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                  })
                }
              />
              <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
              <Tooltip
                labelFormatter={(v: string) =>
                  new Date(v).toLocaleDateString("en-US", {
                    weekday: "short",
                    month: "short",
                    day: "numeric",
                  })
                }
              />
              <Line
                type="monotone"
                dataKey="score"
                stroke="#10b981"
                strokeWidth={2}
                dot={{ r: 3, fill: "#10b981" }}
                activeDot={{ r: 5 }}
                name="Score"
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* ── Top Objections ───────────────────────────────────────── */}
      {scorecard.top_objections.length > 0 && (
        <Card className="p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">
            Top Objections Handled
          </h3>
          <div className="flex flex-wrap gap-2">
            {scorecard.top_objections.map((obj, i) => (
              <Badge key={i} variant="warning">
                {obj}
              </Badge>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
