import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { getSessionToken } from "@/lib/session-cookie";
import { completeChannelConnect } from "@/services/api/channels";

export async function GET(request: NextRequest) {
  const token = await getSessionToken();
  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  const code = request.nextUrl.searchParams.get("code");
  const state = request.nextUrl.searchParams.get("state");
  if (!code || !state) {
    return NextResponse.redirect(new URL("/channels?error=missing_oauth_params", request.url));
  }

  const result = await completeChannelConnect(token, code, state);
  if (!result.ok) {
    return NextResponse.redirect(
      new URL(`/channels?error=${encodeURIComponent(result.message)}`, request.url),
    );
  }

  return NextResponse.redirect(new URL("/channels?connected=1", request.url));
}
