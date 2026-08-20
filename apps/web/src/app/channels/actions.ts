"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { getSessionToken } from "@/lib/session-cookie";
import { disconnectChannel, triggerChannelSync } from "@/services/api/channels";

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
