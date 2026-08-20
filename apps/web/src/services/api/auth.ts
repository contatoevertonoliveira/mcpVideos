import "server-only";

import { getApiInternalUrl } from "@/lib/env";
import type { ApiError, AuthResponse, RegisterResponse } from "@/types/auth";

export type ApiResult<T> = { ok: true; data: T } | { ok: false; message: string };

async function postJson<T>(path: string, body: unknown, token?: string): Promise<ApiResult<T>> {
  try {
    const response = await fetch(`${getApiInternalUrl()}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(body),
      cache: "no-store",
    });

    if (!response.ok) {
      const payload = (await response.json().catch(() => null)) as ApiError | null;
      return { ok: false, message: payload?.error?.message ?? "Something went wrong." };
    }

    return { ok: true, data: (await response.json()) as T };
  } catch {
    return { ok: false, message: "Could not reach the server. Please try again." };
  }
}

export function registerUser(payload: {
  email: string;
  name: string;
  password: string;
  organization_name: string;
}): Promise<ApiResult<RegisterResponse>> {
  return postJson<RegisterResponse>("/api/v1/auth/register", payload);
}

export function loginUser(payload: {
  email: string;
  password: string;
}): Promise<ApiResult<AuthResponse>> {
  return postJson<AuthResponse>("/api/v1/auth/login", payload);
}

export async function logoutUser(token: string): Promise<void> {
  await fetch(`${getApiInternalUrl()}/api/v1/auth/logout`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  }).catch(() => undefined);
}

export async function getCurrentUser(token: string): Promise<AuthResponse | null> {
  const response = await fetch(`${getApiInternalUrl()}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  }).catch(() => null);

  if (!response || !response.ok) {
    return null;
  }
  return (await response.json()) as AuthResponse;
}
