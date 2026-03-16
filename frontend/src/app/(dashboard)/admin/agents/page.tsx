"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AgentTable } from "@/components/agents/agent-table";
import { AgentFormModal } from "@/components/agents/agent-form-modal";
import { useToast } from "@/components/ui/toast";
import { QUERY_KEYS, PAGE_SIZE_DEFAULT } from "@/lib/constants";
import {
  getAgents,
  createAgent,
  updateAgent,
  deactivateAgent,
  type CreateAgentPayload,
  type UpdateAgentPayload,
} from "@/lib/agents-api";
import type { AgentPerformance } from "@/types/models";

export default function AdminAgentsPage() {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  // ── Filter / pagination state ──────────────────────────────────────────────
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);

  // ── Modal state ────────────────────────────────────────────────────────────
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingAgent, setEditingAgent] = useState<AgentPerformance | null>(null);

  // ── Queries ────────────────────────────────────────────────────────────────
  const { data, isLoading } = useQuery({
    queryKey: [
      ...QUERY_KEYS.AGENTS,
      { search, roleFilter, statusFilter, page },
    ],
    queryFn: () =>
      getAgents({
        search: search || undefined,
        role: roleFilter as AgentPerformance["role"] | "",
        is_active:
          statusFilter === "active"
            ? true
            : statusFilter === "inactive"
            ? false
            : undefined,
        page,
        page_size: PAGE_SIZE_DEFAULT,
      }),
    placeholderData: (prev) => prev,
  });

  // ── Mutations ──────────────────────────────────────────────────────────────
  const { mutate: createMutation, isPending: isCreating } = useMutation({
    mutationFn: (payload: CreateAgentPayload) => createAgent(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.AGENTS });
      setIsModalOpen(false);
      showToast({ type: "success", title: "Agent created successfully." });
    },
    onError: (err: Error) => {
      showToast({ type: "error", title: "Failed to create agent", message: err.message });
    },
  });

  const { mutate: updateMutation, isPending: isUpdating } = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdateAgentPayload }) =>
      updateAgent(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.AGENTS });
      setIsModalOpen(false);
      setEditingAgent(null);
      showToast({ type: "success", title: "Agent updated successfully." });
    },
    onError: (err: Error) => {
      showToast({ type: "error", title: "Failed to update agent", message: err.message });
    },
  });

  const { mutate: deactivateMutation } = useMutation({
    mutationFn: (id: string) => deactivateAgent(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.AGENTS });
      showToast({ type: "success", title: "Agent deactivated." });
    },
    onError: (err: Error) => {
      showToast({ type: "error", title: "Failed to deactivate agent", message: err.message });
    },
  });

  // ── Handlers ───────────────────────────────────────────────────────────────
  function openCreate() {
    setEditingAgent(null);
    setIsModalOpen(true);
  }

  function openEdit(agent: AgentPerformance) {
    setEditingAgent(agent);
    setIsModalOpen(true);
  }

  function handleModalClose() {
    setIsModalOpen(false);
    setEditingAgent(null);
  }

  function handleModalSubmit(
    payload: CreateAgentPayload | UpdateAgentPayload
  ) {
    if (editingAgent) {
      updateMutation({ id: editingAgent.id, payload });
    } else {
      createMutation(payload as CreateAgentPayload);
    }
  }

  const agents = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = data?.total_pages ?? 1;

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-50 rounded-xl">
            <Users size={22} className="text-blue-600" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-gray-900">Agents</h1>
            <p className="text-sm text-gray-500">
              Manage your team, roles, and performance
            </p>
          </div>
        </div>

        <Button onClick={openCreate} id="add-agent-btn">
          <Plus size={16} />
          Add Agent
        </Button>
      </div>

      {/* Table */}
      <AgentTable
        agents={agents}
        isLoading={isLoading}
        total={total}
        page={page}
        pageSize={PAGE_SIZE_DEFAULT}
        totalPages={totalPages}
        search={search}
        roleFilter={roleFilter}
        statusFilter={statusFilter}
        onSearchChange={(v) => { setSearch(v); setPage(1); }}
        onRoleFilterChange={(v) => { setRoleFilter(v); setPage(1); }}
        onStatusFilterChange={(v) => { setStatusFilter(v); setPage(1); }}
        onPageChange={setPage}
        onEdit={openEdit}
        onDeactivate={(agent) => deactivateMutation(agent.id)}
      />

      {/* Create / Edit Modal */}
      <AgentFormModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        agent={editingAgent}
        onSubmit={handleModalSubmit}
        isSubmitting={isCreating || isUpdating}
      />
    </div>
  );
}
