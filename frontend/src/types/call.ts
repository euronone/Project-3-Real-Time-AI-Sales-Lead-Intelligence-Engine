import type { CallStatus } from "./models";

export interface ActiveCall {
  call_sid: string;
  call_id: string;
  lead_id: string;
  agent_id: string;
  started_at: string;
  status: CallStatus;
}

export interface TranscriptChunk {
  speaker: "agent" | "customer";
  text: string;
  start_time: number;
  end_time: number;
  confidence: number;
}

export interface AiGuidance {
  type: "suggestion" | "warning" | "battle_card" | "question" | "pricing";
  content: string;
  confidence: number;
}

export interface SentimentUpdate {
  score: number;
  label: "positive" | "neutral" | "negative";
  timestamp: number;
}

export interface RedFlagAlert {
  type: string;
  description: string;
  severity: "low" | "medium" | "high";
}

export interface InitiateCallRequest {
  lead_id: string;
}

export interface InitiateCallResponse {
  call_id: string;
  call_sid: string;
  token: string;
}
