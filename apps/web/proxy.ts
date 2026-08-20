import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { SESSION_COOKIE_NAME } from "@/lib/session-cookie-name";

const PROTECTED_PREFIXES = ["/dashboard"];
const AUTH_ONLY_PAGES = ["/login", "/register"];

/**
 * Cookie-presence check only - a fast redirect UX. The real authorization
 * boundary is server-side in each page/action (Documento 02 sec. 18: never
 * trust a single layer), which validates the token against the API.
 */
export function proxy(request: NextRequest) {
  const hasSession = request.cookies.has(SESSION_COOKIE_NAME);
  const { pathname } = request.nextUrl;

  if (PROTECTED_PREFIXES.some((prefix) => pathname.startsWith(prefix)) && !hasSession) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (AUTH_ONLY_PAGES.includes(pathname) && hasSession) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/login", "/register"],
};
