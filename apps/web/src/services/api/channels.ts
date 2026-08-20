import "server-only";

import { getApiInternalUrl } from "@/lib/env";
import type {
  ChannelDNA,
  ChannelIntelligence,
  ChannelStrategyStatus,
  ChannelSummary,
  SourceVideoSummary,
} from "@/types/channel";

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

export async function triggerChannelSync(token: string, channelId: string): Promise<void> {
  await fetch(`${getApiInternalUrl()}/api/v1/channels/${channelId}/sync`, {
    method: "POST",
    headers: authHeaders(token),
    cache: "no-store",
  }).catch(() => undefined);
}

export async function listChannelVideos(
  token: string,
  channelId: string,
): Promise<SourceVideoSummary[]> {
  const response = await fetch(`${getApiInternalUrl()}/api/v1/channels/${channelId}/videos`, {
    headers: authHeaders(token),
    cache: "no-store",
  }).catch(() => null);

  if (!response || !response.ok) {
    return [];
  }
  return (await response.json()) as SourceVideoSummary[];
}

export async function triggerChannelAnalysis(token: string, channelId: string): Promise<void> {
  await fetch(`${getApiInternalUrl()}/api/v1/channels/${channelId}/analyze`, {
    method: "POST",
    headers: authHeaders(token),
    cache: "no-store",
  }).catch(() => undefined);
}

export async function getChannelIntelligence(
  token: string,
  channelId: string,
): Promise<ChannelIntelligence> {
  const response = await fetch(`${getApiInternalUrl()}/api/v1/channels/${channelId}/intelligence`, {
    headers: authHeaders(token),
    cache: "no-store",
  }).catch(() => null);

  if (!response || !response.ok) {
    return { channel_profile: null, audience_profile: null };
  }
  return (await response.json()) as ChannelIntelligence;
}

export async function triggerChannelDNAGeneration(token: string, channelId: string): Promise<void> {
  await fetch(`${getApiInternalUrl()}/api/v1/channels/${channelId}/dna/generate`, {
    method: "POST",
    headers: authHeaders(token),
    cache: "no-store",
  }).catch(() => undefined);
}

export async function getChannelDNA(token: string, channelId: string): Promise<ChannelDNA | null> {
  const response = await fetch(`${getApiInternalUrl()}/api/v1/channels/${channelId}/dna`, {
    headers: authHeaders(token),
    cache: "no-store",
  }).catch(() => null);

  if (!response || !response.ok) {
    return null;
  }
  return (await response.json()) as ChannelDNA | null;
}

export async function triggerChannelStrategyGeneration(
  token: string,
  channelId: string,
): Promise<void> {
  await fetch(`${getApiInternalUrl()}/api/v1/channels/${channelId}/strategy/generate`, {
    method: "POST",
    headers: authHeaders(token),
    cache: "no-store",
  }).catch(() => undefined);
}

export async function getChannelStrategyStatus(
  token: string,
  channelId: string,
): Promise<ChannelStrategyStatus> {
  const response = await fetch(`${getApiInternalUrl()}/api/v1/channels/${channelId}/strategy`, {
    headers: authHeaders(token),
    cache: "no-store",
  }).catch(() => null);

  if (!response || !response.ok) {
    return { active: null, pending_draft: null };
  }
  return (await response.json()) as ChannelStrategyStatus;
}

export async function approveChannelStrategy(
  token: string,
  channelId: string,
  strategyId: string,
): Promise<void> {
  await fetch(`${getApiInternalUrl()}/api/v1/channels/${channelId}/strategy/${strategyId}/approve`, {
    method: "POST",
    headers: authHeaders(token),
    cache: "no-store",
  }).catch(() => undefined);
}
