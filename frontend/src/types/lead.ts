import type { LeadStatus, LeadPriority } from "./models";

export interface LeadFilters {
  status?: LeadStatus;
  priority?: LeadPriority;
  agent_id?: string;
  campaign_id?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

export interface CreateLeadRequest {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  company: string;
  title?: string;
  status?: LeadStatus;
  priority?: LeadPriority;
  source?: string;
  deal_value?: number;
  campaign_id?: string;
  assigned_agent_id?: string;
  custom_fields?: Record<string, unknown>;
}

export interface UpdateLeadRequest extends Partial<CreateLeadRequest> {}

export interface AssignLeadRequest {
  agent_id: string;
}
