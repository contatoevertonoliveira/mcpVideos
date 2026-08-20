"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { getSessionToken } from "@/lib/session-cookie";
import {
  approveChannelStrategy,
  disconnectChannel,
  triggerChannelAnalysis,
  triggerChannelDNAGeneration,
  triggerChannelStrategyGeneration,
  triggerChannelSync,
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
