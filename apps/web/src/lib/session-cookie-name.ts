// Kept in its own module (no "server-only" marker) so both
// lib/session-cookie.ts (Server Components/Actions) and proxy.ts (Proxy
// runtime) can import the same constant without bundling restrictions.
export const SESSION_COOKIE_NAME = "mcp_session";
