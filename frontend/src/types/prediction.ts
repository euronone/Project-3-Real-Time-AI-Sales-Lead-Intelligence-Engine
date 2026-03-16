import type { PredictionConfidence, RedFlag } from "./models";

export type WinProbabilityLevel = "low" | "medium" | "high";

export function getWinProbabilityLevel(probability: number): WinProbabilityLevel {
  if (probability < 30) return "low";
  if (probability < 70) return "medium";
  return "high";
}

export interface PipelineLead {
  lead_id: string;
  lead_name: string;
  company: string;
  deal_value: number | null;
  win_probability: number;
  confidence: PredictionConfidence;
  key_factors: string[];
  red_flags: RedFlag[];
  recommended_actions: string[];
  last_updated: string;
}

export interface PredictionFilters {
  min_probability?: number;
  max_probability?: number;
  confidence?: PredictionConfidence;
}
