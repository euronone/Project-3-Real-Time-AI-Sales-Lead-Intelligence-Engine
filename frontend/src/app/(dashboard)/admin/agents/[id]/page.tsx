"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Edit2 } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar } from "@/components/ui/avatar";
import { AgentScorecard } from "@/components/agents/agent-scorecard";
import { AgentFormModal } from "@/components/agents/agent-form-modal";
import { DeactivateToggle } from "@/components/agents/deactivate-toggle";
import { Skeleton } from "@/components/ui/loading";
import { useToast } from "@/components/ui/toast";
import { QUERY_KEYS } from "@/lib/constants";
import {
  getAgentScorecard,
  updateAgent,
  deactivateAgent,
  type UpdateAgentPayload,
} from "@/lib/agents-api";
import api from "@/lib/api";
import { API_ROUTES } from "@/lib/constants";
import { formatDate } from "@/lib/utils";
import type { AgentPerformance } from "@/types/models";

const ROLE_LABEL: Record<string, string> = {
  super_admin: "Super Admin",
  tenant_admin: "Admin",
  manager: "Manager",
  agent: "Agent",
};

const ROLE_BADGE: Record<string, "info" | "purple" | "neutral"> = {
  super_admin: "info",
  tenant_admin: "info",
  manager: "purple",
  agent: "neutral",
};

export default function AgentDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const agentId = params.id;

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  // ── Fetch agent profile ────────────────────────────────────────────────────
  const { data: agent, isLoading: isAgentLoading } = useQuery<AgentPerformance>({
    queryKey: QUERY_KEYS.USER(agentId),
    queryFn: async () => {
      const { data } = await api.get<AgentPerformance>(API_ROUTES.USER(agentId));
      return data;
    },
  });

  // ── Fetch scorecard ────────────────────────────────────────────────────────
  const { data: scorecard, isLoading: isScorecardLoading } = useQuery({
    queryKey: QUERY_KEYS.AGENT_SCORECARD(agentId),
    queryFn: () => getAgentScorecard(agentId),
  });

  // ── Mutations ──────────────────────────────────────────────────────────────
  const { mutate: updateMutation, isPending: isUpdating } = useMutation({
    mutationFn: (payload: UpdateAgentPayload) =>
      updateAgent(agentId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.USER(agentId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.AGENTS });
      setIsEditModalOpen(false);
      showToast({ type: "success", title: "Agent updated." });
    },
    onError: (err: Error) => {
      showToast({ type: "error", title: err.message });
    },
  });

  const { mutate: deactivateMutation, isPending: isDeactivating } = useMutation({
    mutationFn: () => deactivateAgent(agentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.USER(agentId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.AGENTS });
      showToast({ type: "success", title: "Agent deactivated." });
      router.push("/admin/agents");
    },
    onError: (err: Error) => {
      showToast({ type: "error", title: err.message });
    },
  });

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="flex flex-col gap-6 p-6">
      {/* ── Breadcrumb ─────────────────────────────────────── */}
      <nav className="flex items-center gap-2 text-sm text-gray-500">
        <Link href="/admin" className="hover:text-gray-700 transition-colors">
          Admin
        </Link>
        <span>/</span>
        <Link
          href="/admin/agents"
          className="hover:text-gray-700 transition-colors"
        >
          Agents
        </Link>
        <span>/</span>
        <span className="text-gray-900 font-medium">
          {isAgentLoading ? "…" : agent?.full_name}
        </span>
      </nav>

      {/* ── Back button ────────────────────────────────────── */}
      <Button
        variant="ghost"
        size="sm"
        className="w-fit"
        onClick={() => router.back()}
      >
        <ArrowLeft size={15} />
        Back to Agents
      </Button>

      {/* ── Profile header ─────────────────────────────────── */}
      {isAgentLoading ? (
        <div className="flex items-center gap-5 p-6 rounded-2xl border border-gray-200 bg-white">
          <Skeleton className="w-16 h-16 rounded-full" />
          <div className="flex flex-col gap-2">
            <Skeleton className="h-5 w-48" />
            <Skeleton className="h-4 w-36" />
            <Skeleton className="h-5 w-20" />
          </div>
        </div>
      ) : agent ? (
        <div className="flex flex-wrap items-center gap-5 p-6 rounded-2xl border border-gray-200 bg-white">
          <Avatar name={agent.full_name} size="lg" />

          <div className="flex-1 min-w-0">
            <h1 className="text-xl font-semibold text-gray-900">
              {agent.full_name}
            </h1>
            <p className="text-sm text-gray-500">{agent.email}</p>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <Badge variant={ROLE_BADGE[agent.role]}>
                {ROLE_LABEL[agent.role]}
              </Badge>
              <Badge variant={agent.is_active ? "success" : "neutral"} dot>
                {agent.is_active ? "Active" : "Inactive"}
              </Badge>
              <span className="text-xs text-gray-400">
                Joined {formatDate(agent.created_at)}
              </span>
              {agent.last_login && (
                <span className="text-xs text-gray-400">
                  · Last login {formatDate(agent.last_login)}
                </span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-3 ml-auto">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsEditModalOpen(true)}
            >
              <Edit2 size={14} />
              Edit
            </Button>
            <DeactivateToggle
              isActive={agent.is_active}
              agentName={agent.full_name}
              isPending={isDeactivating}
              onConfirm={() => deactivateMutation()}
            />
          </div>
        </div>
      ) : (
        <p className="text-gray-500 text-sm">Agent not found.</p>
      )}

      {/* ── Scorecard ──────────────────────────────────────── */}
      <div>
        <h2 className="text-base font-semibold text-gray-800 mb-4">
          Performance Scorecard
        </h2>
        <AgentScorecard scorecard={scorecard} isLoading={isScorecardLoading} />
      </div>

      {/* ── Edit Modal ─────────────────────────────────────── */}
      <AgentFormModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        agent={agent}
        onSubmit={(payload) => updateMutation(payload as UpdateAgentPayload)}
        isSubmitting={isUpdating}
      />
    </div>
  );
}
