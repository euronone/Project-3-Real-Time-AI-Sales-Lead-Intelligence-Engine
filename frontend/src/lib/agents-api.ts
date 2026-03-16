import api from "./api";
import { API_ROUTES } from "./constants";
import type { AgentPerformance, AgentScorecard, UserRole } from "@/types/models";

// ── Query params ─────────────────────────────────────────────────────────────

export interface GetAgentsParams {
  search?: string;
  role?: UserRole | "";
  is_active?: boolean | "";
  page?: number;
  page_size?: number;
}

// ── Mutation payloads ────────────────────────────────────────────────────────

export interface CreateAgentPayload {
  full_name: string;
  email: string;
  role: UserRole;
  phone?: string;
}

export interface UpdateAgentPayload {
  full_name?: string;
  email?: string;
  role?: UserRole;
  phone?: string;
}

// ── Paginated response wrapper ───────────────────────────────────────────────

export interface PaginatedAgents {
  items: AgentPerformance[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ── API functions ────────────────────────────────────────────────────────────

/** GET /api/v1/agents — List agents with basic performance metrics */
export async function getAgents(
  params: GetAgentsParams = {}
): Promise<PaginatedAgents> {
  // Remove undefined / empty-string params so the server doesn't receive them
  const cleaned = Object.fromEntries(
    Object.entries(params).filter(([, v]) => v !== undefined && v !== "")
  );
  const { data } = await api.get<PaginatedAgents>(API_ROUTES.AGENTS, {
    params: cleaned,
  });
  return data;
}

/** POST /api/v1/users — Create a new agent/user in the tenant */
export async function createAgent(
  payload: CreateAgentPayload
): Promise<AgentPerformance> {
  const { data } = await api.post<AgentPerformance>(
    API_ROUTES.USERS,
    payload
  );
  return data;
}

/** PATCH /api/v1/users/{id} — Update user fields */
export async function updateAgent(
  id: string,
  payload: UpdateAgentPayload
): Promise<AgentPerformance> {
  const { data } = await api.patch<AgentPerformance>(
    API_ROUTES.USER(id),
    payload
  );
  return data;
}

/** DELETE /api/v1/users/{id} — Deactivate (soft-delete) a user */
export async function deactivateAgent(id: string): Promise<void> {
  await api.delete(API_ROUTES.USER(id));
}

/** GET /api/v1/agents/{id}/scorecard — Fetch agent performance scorecard */
export async function getAgentScorecard(
  id: string
): Promise<AgentScorecard> {
  const { data } = await api.get<AgentScorecard>(
    API_ROUTES.AGENT_SCORECARD(id)
  );
  return data;
}
