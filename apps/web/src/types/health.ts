export interface HealthResponse {
  data: {
    status: string;
    component?: string;
  };
  meta: Record<string, unknown>;
}
