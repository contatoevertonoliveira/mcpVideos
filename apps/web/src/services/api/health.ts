import { getApiInternalUrl } from "@/lib/env";
import type { HealthResponse } from "@/types/health";

export type ApiConnection =
  | { ok: true; health: HealthResponse }
  | { ok: false; error: string };

/**
 * Checks API connectivity from the Next.js server. This is a Foundation
 * (Fase 01) sanity check, not the app's real API client - a shared,
 * feature-oriented client arrives with the first real feature (Fase 03+).
 */
export async function checkApiConnection(): Promise<ApiConnection> {
  try {
    const response = await fetch(`${getApiInternalUrl()}/health`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return { ok: false, error: `API respondeu com status ${response.status}` };
    }

    const health = (await response.json()) as HealthResponse;
    return { ok: true, health };
  } catch {
    return { ok: false, error: "Não foi possível conectar à API." };
  }
}
