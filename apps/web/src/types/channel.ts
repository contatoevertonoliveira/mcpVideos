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
