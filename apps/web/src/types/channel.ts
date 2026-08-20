export type ConnectionStatus =
  | "connected"
  | "needs_reauthorization"
  | "syncing"
  | "error"
  | "disconnected"
  | null;

export interface ChannelSummary {
  id: string;
  organization_id: string;
  platform: "youtube";
  external_channel_id: string | null;
  name: string;
  handle: string | null;
  status: "pending" | "active" | "disabled";
  automation_mode: "manual" | "assisted" | "semi_auto" | "autopilot";
  connected_at: string | null;
  last_synced_at: string | null;
  connection_status: ConnectionStatus;
}

export interface SourceVideoSummary {
  id: string;
  channel_id: string;
  external_video_id: string;
  title: string;
  video_type: "short" | "long_form" | "live" | "unknown";
  duration_seconds: number | null;
  published_at: string | null;
  thumbnail_url: string | null;
}

export interface ChannelProfileSummary {
  primary_language: string | null;
  primary_category: string | null;
  estimated_audience: string | null;
  content_summary: string | null;
  confidence: number;
  generated_at: string;
}

export interface ChannelIntelligence {
  channel_profile: ChannelProfileSummary | null;
  audience_profile: { confidence: number } | null;
}

export interface ChannelDNA {
  version: number;
  status: "draft" | "active" | "superseded";
  confidence: number;
  content_patterns_json: { content_patterns?: string[] };
  performance_patterns_json: { high_performing_patterns?: string[]; low_performing_patterns?: string[] };
  publishing_patterns_json: { publishing_patterns?: string[] };
  activated_at: string | null;
}

export interface ContentPillarSummary {
  id: string;
  name: string;
  description: string | null;
  target_ratio: number;
  priority: number;
  active: boolean;
}

export interface ContentStrategySummary {
  id: string;
  version: number;
  status: "draft" | "active" | "archived";
  objective: string;
  shorts_ratio: number;
  long_form_ratio: number;
  experimental_ratio: number;
  recommended_frequency_json: Record<string, string>;
  strategy_json: { recommendations?: string[] };
  pillars: ContentPillarSummary[];
}

export interface ChannelStrategyStatus {
  active: ContentStrategySummary | null;
  pending_draft: ContentStrategySummary | null;
}
