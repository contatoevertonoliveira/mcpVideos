import "server-only";

import { getApiInternalUrl } from "@/lib/env";
import type { ChannelSummary } from "@/types/channel";

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

export async function listChannels(token: string): Promise<ChannelSummary[]> {
  const response = await fetch(`${getApiInternalUrl()}/api/v1/channels`, {
    headers: authHeaders(token),
    cache: "no-store",
  }).catch(() => null);

  if (!response || !response.ok) {
    return [];
  }
  return (await response.json()) as ChannelSummary[];
}

export async function startChannelConnect(token: string): Promise<string | null> {
  const response = await fetch(`${getApiInternalUrl()}/api/v1/channels/connect`, {
    method: "POST",
    headers: authHeaders(token),
    cache: "no-store",
  }).catch(() => null);

  if (!response || !response.ok) {
    return null;
  }
  const body = (await response.json()) as { authorization_url: string };
  return body.authorization_url;
}

export async function completeChannelConnect(
  token: string,
  code: string,
  state: string,
): Promise<{ ok: true } | { ok: false; message: string }> {
  const response = await fetch(`${getApiInternalUrl()}/api/v1/channels/callback`, {
    method: "POST",
    headers: { ...authHeaders(token), "Content-Type": "application/json" },
    body: JSON.stringify({ code, state }),
    cache: "no-store",
  }).catch(() => null);

  if (!response || !response.ok) {
    const payload = await response?.json().catch(() => null);
    return { ok: false, message: payload?.error?.message ?? "Could not connect the channel." };
  }
  return { ok: true };
}

export async function disconnectChannel(token: string, channelId: string): Promise<void> {
  await fetch(`${getApiInternalUrl()}/api/v1/channels/${channelId}/disconnect`, {
    method: "POST",
    headers: authHeaders(token),
    cache: "no-store",
  }).catch(() => undefined);
}
