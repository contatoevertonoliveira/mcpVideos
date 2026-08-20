import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
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
      className={`dark ${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body className="min-h-full flex flex-col bg-background text-foreground">{children}</body>
    </html>
  );
}
