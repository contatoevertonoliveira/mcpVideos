import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { getSessionToken } from "@/lib/session-cookie";
import { startChannelConnect } from "@/services/api/channels";

export async function GET(request: NextRequest) {
  const token = await getSessionToken();
  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  const authorizationUrl = await startChannelConnect(token);
  if (!authorizationUrl) {
    return NextResponse.redirect(new URL("/channels?error=connect_failed", request.url));
  }

  return NextResponse.redirect(authorizationUrl);
}
