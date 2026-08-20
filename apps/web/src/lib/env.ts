/**
 * Server-side URL used to reach the API from within the Next.js server
 * (e.g. the "api" service name inside docker compose). Never exposed to the
 * browser bundle.
 */
export function getApiInternalUrl(): string {
  return process.env.API_INTERNAL_URL ?? "http://localhost:8000";
}
