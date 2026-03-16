"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { Search, MoreHorizontal, Edit2, UserX, Eye } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Pagination } from "@/components/ui/pagination";
import { Avatar } from "@/components/ui/avatar";
import { Dropdown } from "@/components/ui/dropdown";
import { cn } from "@/lib/utils";
import { debounce, formatDate, formatDuration } from "@/lib/utils";
import type { AgentPerformance, UserRole } from "@/types/models";

// ── Constants ────────────────────────────────────────────────────────────────

const ROLE_OPTIONS = [
  { value: "", label: "All Roles" },
  { value: "tenant_admin", label: "Admin" },
  { value: "manager", label: "Manager" },
  { value: "agent", label: "Agent" },
];

const STATUS_OPTIONS = [
  { value: "", label: "All Statuses" },
  { value: "active", label: "Active" },
  { value: "inactive", label: "Inactive" },
];

const ROLE_BADGE_MAP: Record<UserRole, "info" | "purple" | "warning" | "neutral"> = {
  super_admin: "info",
  tenant_admin: "info",
  manager: "purple",
  agent: "neutral",
};

const ROLE_LABEL_MAP: Record<UserRole, string> = {
  super_admin: "Super Admin",
  tenant_admin: "Admin",
  manager: "Manager",
  agent: "Agent",
};

// ── Props ────────────────────────────────────────────────────────────────────

interface AgentTableProps {
  agents: AgentPerformance[];
  isLoading?: boolean;
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  search: string;
  roleFilter: string;
  statusFilter: string;
  onSearchChange: (v: string) => void;
  onRoleFilterChange: (v: string) => void;
  onStatusFilterChange: (v: string) => void;
  onPageChange: (p: number) => void;
  onEdit: (agent: AgentPerformance) => void;
  onDeactivate: (agent: AgentPerformance) => void;
}

// ── Component ────────────────────────────────────────────────────────────────

export function AgentTable({
  agents,
  isLoading,
  total,
  page,
  pageSize,
  totalPages,
  search,
  roleFilter,
  statusFilter,
  onSearchChange,
  onRoleFilterChange,
  onStatusFilterChange,
  onPageChange,
  onEdit,
  onDeactivate,
}: AgentTableProps) {
  // Debounce search so we don't fire a query on every keystroke
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const debouncedSearch = useCallback(debounce(onSearchChange, 300), []);

  const [localSearch, setLocalSearch] = useState(search);

  function handleSearchInput(val: string) {
    setLocalSearch(val);
    debouncedSearch(val);
  }

  return (
    <div className="flex flex-col gap-4">
      {/* ── Filter bar ─────────────────────────────────────── */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex-1 min-w-48">
          <Input
            id="agent-search"
            placeholder="Search by name or email…"
            value={localSearch}
            onChange={(e) => handleSearchInput(e.target.value)}
            leftIcon={<Search size={15} />}
          />
        </div>

        <div className="w-40">
          <Select
            id="agent-role-filter"
            options={ROLE_OPTIONS}
            value={roleFilter}
            onChange={(e) => onRoleFilterChange(e.target.value)}
            aria-label="Filter by role"
          />
        </div>

        <div className="w-44">
          <Select
            id="agent-status-filter"
            options={STATUS_OPTIONS}
            value={statusFilter}
            onChange={(e) => onStatusFilterChange(e.target.value)}
            aria-label="Filter by status"
          />
        </div>

        <p className="ml-auto text-sm text-gray-500 whitespace-nowrap">
          {total} agent{total !== 1 ? "s" : ""}
        </p>
      </div>

      {/* ── Table ──────────────────────────────────────────── */}
      <Table
        isLoading={isLoading}
        emptyMessage={agents.length === 0 && !isLoading ? "No agents found." : undefined}
      >
        <TableHeader>
          <tr>
            <TableHead>Agent</TableHead>
            <TableHead>Role</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Calls</TableHead>
            <TableHead>Avg Duration</TableHead>
            <TableHead>Conversion</TableHead>
            <TableHead>Score</TableHead>
            <TableHead>Last Login</TableHead>
            <TableHead className="w-10" />
          </tr>
        </TableHeader>

        <TableBody>
          {agents.map((agent) => (
            <TableRow key={agent.id}>
              {/* Agent name + email */}
              <TableCell>
                <div className="flex items-center gap-3">
                  <Avatar name={agent.full_name} size="sm" />
                  <div className="min-w-0">
                    <Link
                      href={`/admin/agents/${agent.id}`}
                      className="block font-medium text-gray-900 hover:text-blue-600 truncate transition-colors"
                    >
                      {agent.full_name}
                    </Link>
                    <span className="block text-xs text-gray-500 truncate">
                      {agent.email}
                    </span>
                  </div>
                </div>
              </TableCell>

              {/* Role */}
              <TableCell>
                <Badge variant={ROLE_BADGE_MAP[agent.role]}>
                  {ROLE_LABEL_MAP[agent.role]}
                </Badge>
              </TableCell>

              {/* Status */}
              <TableCell>
                <Badge variant={agent.is_active ? "success" : "neutral"} dot>
                  {agent.is_active ? "Active" : "Inactive"}
                </Badge>
              </TableCell>

              {/* Stats */}
              <TableCell>
                <span className="font-medium">{agent.total_calls}</span>
              </TableCell>
              <TableCell>
                {formatDuration(agent.avg_call_duration)}
              </TableCell>
              <TableCell>
                <span
                  className={cn(
                    "font-medium",
                    agent.conversion_rate >= 50
                      ? "text-green-600"
                      : agent.conversion_rate >= 25
                      ? "text-yellow-600"
                      : "text-red-600"
                  )}
                >
                  {agent.conversion_rate.toFixed(1)}%
                </span>
              </TableCell>
              <TableCell>
                <span
                  className={cn(
                    "font-medium",
                    agent.avg_agent_score >= 80
                      ? "text-green-600"
                      : agent.avg_agent_score >= 60
                      ? "text-yellow-600"
                      : "text-red-600"
                  )}
                >
                  {agent.avg_agent_score.toFixed(0)}
                </span>
              </TableCell>

              {/* Last login */}
              <TableCell>
                <span className="text-gray-500 text-xs">
                  {agent.last_login ? formatDate(agent.last_login) : "Never"}
                </span>
              </TableCell>

              {/* Actions */}
              <TableCell>
                <Dropdown
                  trigger={
                    <Button
                      variant="ghost"
                      size="sm"
                      className="p-1 h-7 w-7"
                      aria-label={`Actions for ${agent.full_name}`}
                    >
                      <MoreHorizontal size={16} />
                    </Button>
                  }
                  items={[
                    {
                      label: "View Detail",
                      icon: <Eye size={14} />,
                      href: `/admin/agents/${agent.id}`,
                    },
                    {
                      label: "Edit",
                      icon: <Edit2 size={14} />,
                      onClick: () => onEdit(agent),
                    },
                    {
                      label: agent.is_active ? "Deactivate" : "Reactivate",
                      icon: <UserX size={14} />,
                      onClick: () => onDeactivate(agent),
                      className: agent.is_active ? "text-red-600" : undefined,
                    },
                  ]}
                />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* ── Pagination ─────────────────────────────────────── */}
      {totalPages > 1 && (
        <Pagination
          currentPage={page}
          totalPages={totalPages}
          pageSize={pageSize}
          totalItems={total}
          onPageChange={onPageChange}
        />
      )}
    </div>
  );
}
