// Enums — mirror backend Pydantic enums exactly
export type UserRole = "super_admin" | "tenant_admin" | "manager" | "agent";
export type LeadStatus = "new" | "contacted" | "qualified" | "proposal" | "negotiation" | "won" | "lost";
export type LeadPriority = "low" | "medium" | "high" | "urgent";
export type CallStatus = "initiated" | "ringing" | "in_progress" | "completed" | "failed" | "no_answer";
export type CallDirection = "inbound" | "outbound";
export type PredictionConfidence = "low" | "medium" | "high";
export type CampaignStatus = "draft" | "active" | "paused" | "completed";
export type TenantPlan = "free" | "starter" | "pro" | "enterprise";

// Core domain models
export interface Tenant {
  id: string;
  name: string;
  slug: string;
  plan: TenantPlan;
  settings: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  tenant_id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  last_login: string | null;
  created_at: string;
}

export interface Lead {
  id: string;
  tenant_id: string;
  assigned_agent_id: string | null;
  campaign_id: string | null;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  company: string;
  title: string;
  status: LeadStatus;
  priority: LeadPriority;
  source: string;
  deal_value: number | null;
  custom_fields: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Call {
  id: string;
  tenant_id: string;
  agent_id: string;
  lead_id: string;
  twilio_call_sid: string;
  direction: CallDirection;
  status: CallStatus;
  duration_seconds: number | null;
  recording_url: string | null;
  recording_sid: string | null;
  disposition: string | null;
  started_at: string | null;
  ended_at: string | null;
  created_at: string;
}

export interface CallTranscript {
  id: string;
  call_id: string;
  speaker: "agent" | "customer";
  text: string;
  start_time: number;
  end_time: number;
  confidence: number;
  created_at: string;
}

export interface CallAnalysis {
  id: string;
  call_id: string;
  summary: string;
  sentiment_overall: number;
  sentiment_timeline: Array<{ time: number; score: number }>;
  topics: string[];
  objections: Array<{ type: string; text: string }>;
  key_moments: Array<{ time: number; description: string; type: string }>;
  talk_ratio_agent: number;
  filler_word_count: number;
  agent_score: number;
  feedback: string;
  red_flags: RedFlag[];
  action_items: string[];
  created_at: string;
}

export interface DealPrediction {
  id: string;
  lead_id: string;
  call_id: string | null;
  win_probability: number;
  confidence: PredictionConfidence;
  key_factors: string[];
  red_flags: RedFlag[];
  recommended_actions: string[];
  reasoning: string;
  created_at: string;
}

export interface RedFlag {
  type: string;
  description: string;
  severity: "low" | "medium" | "high";
}

export interface Campaign {
  id: string;
  tenant_id: string;
  name: string;
  description: string;
  script_template: string;
  status: CampaignStatus;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
}

export interface LeadFlow {
  id: string;
  tenant_id: string;
  name: string;
  description: string;
  flow_definition: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Notification {
  id: string;
  tenant_id: string;
  user_id: string;
  type: string;
  title: string;
  message: string;
  data: Record<string, unknown>;
  is_read: boolean;
  created_at: string;
}

export interface AuditLog {
  id: string;
  tenant_id: string;
  user_id: string;
  action: string;
  entity_type: string;
  entity_id: string;
  changes: Record<string, unknown>;
  ip_address: string;
  created_at: string;
}

export interface Webhook {
  id: string;
  tenant_id: string;
  url: string;
  events: string[];
  is_active: boolean;
  created_at: string;
}

export interface AgentPerformance extends User {
  total_calls: number;
  avg_call_duration: number;
  conversion_rate: number;
  avg_agent_score: number;
  total_deals_won: number;
}

export interface AgentScorecard {
  agent_id: string;
  period_days: number;
  total_calls: number;
  avg_call_duration: number; // seconds
  conversion_rate: number;   // 0–100 %
  avg_agent_score: number;   // 0–100
  total_deals_won: number;
  top_objections: string[];
  call_trend: Array<{ date: string; count: number }>;
  score_trend: Array<{ date: string; score: number }>;
}
