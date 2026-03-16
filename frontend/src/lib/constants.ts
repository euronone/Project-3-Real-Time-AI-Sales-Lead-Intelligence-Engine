import type { BadgeProps } from "../types/ui";

// Lead status options with display config
export const LEAD_STATUSES = [
  { value: "new", label: "New", badgeVariant: "info" as BadgeProps },
  { value: "contacted", label: "Contacted", badgeVariant: "neutral" as BadgeProps },
  { value: "qualified", label: "Qualified", badgeVariant: "purple" as BadgeProps },
  { value: "proposal", label: "Proposal", badgeVariant: "warning" as BadgeProps },
  { value: "negotiation", label: "Negotiation", badgeVariant: "warning" as BadgeProps },
  { value: "won", label: "Won", badgeVariant: "success" as BadgeProps },
  { value: "lost", label: "Lost", badgeVariant: "danger" as BadgeProps },
] as const;

// Lead priority options
export const LEAD_PRIORITIES = [
  { value: "low", label: "Low", badgeVariant: "neutral" as BadgeProps },
  { value: "medium", label: "Medium", badgeVariant: "info" as BadgeProps },
  { value: "high", label: "High", badgeVariant: "warning" as BadgeProps },
  { value: "urgent", label: "Urgent", badgeVariant: "danger" as BadgeProps },
] as const;

// Call status options
export const CALL_STATUSES = [
  { value: "initiated", label: "Initiated", badgeVariant: "info" as BadgeProps },
  { value: "ringing", label: "Ringing", badgeVariant: "info" as BadgeProps },
  { value: "in_progress", label: "In Progress", badgeVariant: "success" as BadgeProps },
  { value: "completed", label: "Completed", badgeVariant: "neutral" as BadgeProps },
  { value: "failed", label: "Failed", badgeVariant: "danger" as BadgeProps },
  { value: "no_answer", label: "No Answer", badgeVariant: "warning" as BadgeProps },
] as const;

// User roles
export const USER_ROLES = [
  { value: "super_admin", label: "Super Admin" },
  { value: "tenant_admin", label: "Admin" },
  { value: "manager", label: "Manager" },
  { value: "agent", label: "Agent" },
] as const;

// Socket.IO event names — do not rename without coordinating backend
export const SOCKET_EVENTS = {
  // Client → Server
  JOIN_CALL_ROOM: "join_call_room",
  LEAVE_CALL_ROOM: "leave_call_room",
  // Server → Client
  TRANSCRIPT_CHUNK: "transcript_chunk",
  AI_GUIDANCE: "ai_guidance",
  SENTIMENT_UPDATE: "sentiment_update",
  RED_FLAG_ALERT: "red_flag_alert",
  CALL_STATUS_CHANGED: "call_status_changed",
  NOTIFICATION: "notification",
  DEAL_PREDICTION_UPDATED: "deal_prediction_updated",
} as const;

// TanStack Query cache keys
export const QUERY_KEYS = {
  ME: ["me"] as const,
  USERS: ["users"] as const,
  USER: (id: string) => ["users", id] as const,
  AGENTS: ["agents"] as const,
  AGENT_SCORECARD: (id: string) => ["agents", id, "scorecard"] as const,
  LEADS: ["leads"] as const,
  LEAD: (id: string) => ["leads", id] as const,
  CALLS: ["calls"] as const,
  CALL: (id: string) => ["calls", id] as const,
  CALL_TRANSCRIPT: (id: string) => ["calls", id, "transcript"] as const,
  CALL_ANALYSIS: (id: string) => ["calls", id, "analysis"] as const,
  CAMPAIGNS: ["campaigns"] as const,
  CAMPAIGN: (id: string) => ["campaigns", id] as const,
  LEAD_FLOWS: ["lead-flows"] as const,
  LEAD_FLOW: (id: string) => ["lead-flows", id] as const,
  PREDICTIONS_PIPELINE: ["predictions", "pipeline"] as const,
  LEAD_PREDICTIONS: (leadId: string) => ["predictions", "lead", leadId] as const,
  ANALYTICS_DASHBOARD: ["analytics", "dashboard"] as const,
  ANALYTICS_FUNNEL: ["analytics", "conversion-funnel"] as const,
  ANALYTICS_LEADERBOARD: ["analytics", "agent-leaderboard"] as const,
  NOTIFICATIONS: ["notifications"] as const,
} as const;

// Backend API route paths
export const API_ROUTES = {
  AUTH: {
    LOGIN: "/api/v1/auth/login",
    REGISTER: "/api/v1/auth/register",
    REFRESH: "/api/v1/auth/refresh",
    FORGOT_PASSWORD: "/api/v1/auth/forgot-password",
    RESET_PASSWORD: "/api/v1/auth/reset-password",
  },
  USERS: "/api/v1/users",
  USER: (id: string) => `/api/v1/users/${id}`,
  AGENTS: "/api/v1/agents",
  AGENT_SCORECARD: (id: string) => `/api/v1/agents/${id}/scorecard`,
  LEADS: "/api/v1/leads",
  LEAD: (id: string) => `/api/v1/leads/${id}`,
  LEAD_ASSIGN: (id: string) => `/api/v1/leads/${id}/assign`,
  LEADS_IMPORT: "/api/v1/leads/import",
  CALLS: "/api/v1/calls",
  CALL: (id: string) => `/api/v1/calls/${id}`,
  CALL_TRANSCRIPT: (id: string) => `/api/v1/calls/${id}/transcript`,
  CALL_ANALYSIS: (id: string) => `/api/v1/calls/${id}/analysis`,
  CALL_RECORDING: (id: string) => `/api/v1/calls/${id}/recording`,
  CALL_DISPOSITION: (id: string) => `/api/v1/calls/${id}/disposition`,
  CALL_INITIATE: "/api/v1/calls/initiate",
  CALL_TOKEN: "/api/v1/calls/token",
  CAMPAIGNS: "/api/v1/campaigns",
  CAMPAIGN: (id: string) => `/api/v1/campaigns/${id}`,
  LEAD_FLOWS: "/api/v1/lead-flows",
  LEAD_FLOW: (id: string) => `/api/v1/lead-flows/${id}`,
  ANALYTICS: {
    DASHBOARD: "/api/v1/analytics/dashboard",
    FUNNEL: "/api/v1/analytics/conversion-funnel",
    LEADERBOARD: "/api/v1/analytics/agent-leaderboard",
    CALL_TRENDS: "/api/v1/analytics/call-trends",
    PREDICTION_ACCURACY: "/api/v1/analytics/prediction-accuracy",
  },
  PREDICTIONS: {
    PIPELINE: "/api/v1/predictions/pipeline",
    LEAD: (leadId: string) => `/api/v1/predictions/lead/${leadId}`,
    LEAD_REFRESH: (leadId: string) => `/api/v1/predictions/lead/${leadId}/refresh`,
  },
  NOTIFICATIONS: "/api/v1/notifications",
  NOTIFICATION_READ: (id: string) => `/api/v1/notifications/${id}/read`,
  NOTIFICATIONS_READ_ALL: "/api/v1/notifications/read-all",
  TENANT_SETTINGS: "/api/v1/tenant/settings",
  AUDIT_LOG: "/api/v1/tenant/audit-log",
} as const;

export const PAGE_SIZE_DEFAULT = 20;
