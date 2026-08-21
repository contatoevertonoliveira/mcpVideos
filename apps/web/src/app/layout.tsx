import type { Metadata } from "next";
import { Geist_Mono, Poppins } from "next/font/google";
import "./globals.css";

// Poppins is the app's default typeface (Documento 08B sec. 15: geometric
// sans, matches the Stitch baseline's headline weight/character better than
// Geist). Kept on the same "--font-geist-sans" CSS variable name so
// globals.css's --font-sans -> --font-geist-sans mapping (@theme inline)
// needs no changes.
const bodyFont = Poppins({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "mcp_videos",
  description: "Content Intelligence + Production + Growth Automation",
};

// Dark Mode Premium is the default theme (Documento 08A sec. 6, 153-155) -
// <html> renders with the "dark" class server-side so there is no flash of
// the light palette. This tiny inline script only needs to *remove* it when
// the user has explicitly chosen light before, and must run before paint.
const THEME_INIT_SCRIPT = `
  try {
    if (localStorage.getItem("mcp-videos-theme") === "light") {
      document.documentElement.classList.remove("dark");
    }
  } catch (e) {}
`;

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="pt-BR"
      className={`dark ${bodyFont.variable} ${geistMono.variable} h-full antialiased`}
      // The no-FOUC script below removes "dark" before paint when the user
      // has saved a light preference, which legitimately makes the real DOM
      // disagree with this element's initial server-rendered className.
      // That's the intended behavior, not a bug - suppress React's
      // hydration warning for it instead of letting it misreport a real
      // defect (same fix pattern used by next-themes for this exact case).
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body className="min-h-full flex flex-col bg-background text-foreground">{children}</body>
    </html>
  );
}
