"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { getSessionToken } from "@/lib/session-cookie";
import {
  approveCalendarItem,
  approveChannelIdea,
  approveChannelStrategy,
  disconnectChannel,
  rejectCalendarItem,
  rescheduleCalendarItem,
  triggerCalendarGeneration,
  triggerChannelAnalysis,
  triggerChannelDNAGeneration,
  triggerChannelStrategyGeneration,
  triggerChannelSync,
  triggerIdeaGeneration,
} from "@/services/api/channels";

export async function disconnectChannelAction(formData: FormData): Promise<void> {
  const token = await getSessionToken();
  if (!token) {
    redirect("/login");
  }

  const channelId = String(formData.get("channel_id") ?? "");
  if (!channelId) {
    return;
  }

  await disconnectChannel(token, channelId);
  revalidatePath("/channels");
}

export async function triggerSyncAction(formData: FormData): Promise<void> {
  const token = await getSessionToken();
  if (!token) {
    redirect("/login");
  }

  const channelId = String(formData.get("channel_id") ?? "");
  if (!channelId) {
    return;
  }

  await triggerChannelSync(token, channelId);
  revalidatePath("/channels");
}

export async function triggerAnalysisAction(formData: FormData): Promise<void> {
  const token = await getSessionToken();
  if (!token) {
    redirect("/login");
  }

  const channelId = String(formData.get("channel_id") ?? "");
  if (!channelId) {
    return;
  }

  await triggerChannelAnalysis(token, channelId);
  revalidatePath("/channels");
}

export async function triggerDNAGenerationAction(formData: FormData): Promise<void> {
  const token = await getSessionToken();
  if (!token) {
    redirect("/login");
  }

  const channelId = String(formData.get("channel_id") ?? "");
  if (!channelId) {
    return;
  }

  await triggerChannelDNAGeneration(token, channelId);
  revalidatePath("/channels");
}

export async function triggerStrategyGenerationAction(formData: FormData): Promise<void> {
  const token = await getSessionToken();
  if (!token) {
    redirect("/login");
  }

  const channelId = String(formData.get("channel_id") ?? "");
  if (!channelId) {
    return;
  }

  await triggerChannelStrategyGeneration(token, channelId);
  revalidatePath("/channels");
}

export async function approveStrategyAction(formData: FormData): Promise<void> {
  const token = await getSessionToken();
  if (!token) {
    redirect("/login");
  }

  const channelId = String(formData.get("channel_id") ?? "");
  const strategyId = String(formData.get("strategy_id") ?? "");
  if (!channelId || !strategyId) {
    return;
  }

  await approveChannelStrategy(token, channelId, strategyId);
  revalidatePath("/channels");
}

export async function triggerIdeaGenerationAction(formData: FormData): Promise<void> {
  const token = await getSessionToken();
  if (!token) {
    redirect("/login");
  }

  const channelId = String(formData.get("channel_id") ?? "");
  if (!channelId) {
    return;
  }

  await triggerIdeaGeneration(token, channelId);
  revalidatePath("/ideas");
}

export async function approveIdeaAction(formData: FormData): Promise<void> {
  const token = await getSessionToken();
  if (!token) {
    redirect("/login");
  }

  const channelId = String(formData.get("channel_id") ?? "");
  const ideaId = String(formData.get("idea_id") ?? "");
  if (!channelId || !ideaId) {
    return;
  }

  await approveChannelIdea(token, channelId, ideaId);
  revalidatePath("/ideas");
}

export async function triggerCalendarGenerationAction(formData: FormData): Promise<void> {
  const token = await getSessionToken();
  if (!token) {
    redirect("/login");
  }

  const channelId = String(formData.get("channel_id") ?? "");
  if (!channelId) {
    return;
  }

  await triggerCalendarGeneration(token, channelId);
  revalidatePath("/calendar");
}

export async function approveCalendarItemAction(formData: FormData): Promise<void> {
  const token = await getSessionToken();
  if (!token) {
    redirect("/login");
  }

  const channelId = String(formData.get("channel_id") ?? "");
  const itemId = String(formData.get("item_id") ?? "");
  if (!channelId || !itemId) {
    return;
  }

  await approveCalendarItem(token, channelId, itemId);
  revalidatePath("/calendar");
}

export async function rejectCalendarItemAction(formData: FormData): Promise<void> {
  const token = await getSessionToken();
  if (!token) {
    redirect("/login");
  }

  const channelId = String(formData.get("channel_id") ?? "");
  const itemId = String(formData.get("item_id") ?? "");
  if (!channelId || !itemId) {
    return;
  }

  await rejectCalendarItem(token, channelId, itemId);
  revalidatePath("/calendar");
}

export async function rescheduleCalendarItemAction(formData: FormData): Promise<void> {
  const token = await getSessionToken();
  if (!token) {
    redirect("/login");
  }

  const channelId = String(formData.get("channel_id") ?? "");
  const itemId = String(formData.get("item_id") ?? "");
  const plannedAtLocal = String(formData.get("planned_at") ?? "");
  if (!channelId || !itemId || !plannedAtLocal) {
    return;
  }

  const plannedAt = new Date(plannedAtLocal);
  if (Number.isNaN(plannedAt.getTime())) {
    return;
  }

  await rescheduleCalendarItem(token, channelId, itemId, plannedAt.toISOString());
  revalidatePath("/calendar");
}
