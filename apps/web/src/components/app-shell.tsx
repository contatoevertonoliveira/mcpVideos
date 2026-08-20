"use client";

import { LayoutDashboard, LogOut, Radio, Sparkles } from "lucide-react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { Button } from "@/components/ui/button";

// ssr:false: the toggle reads the DOM's current theme class on mount (set
// by the no-FOUC inline script in layout.tsx before hydration), which
// would otherwise risk a hydration mismatch if server-rendered.
const ThemeToggle = dynamic(
  () => import("@/components/theme-toggle").then((mod) => mod.ThemeToggle),
  { ssr: false, loading: () => <Button variant="ghost" size="icon" disabled aria-hidden /> },
);

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/channels", label: "Canais", icon: Radio },
];

export function AppShell({
  children,
  userName,
  userEmail,
  organizationName,
  logoutAction,
}: {
  children: ReactNode;
  userName: string;
  userEmail: string;
  organizationName: string | null;
  logoutAction: () => void;
}) {
  const pathname = usePathname();

  return (
    <div className="flex min-h-svh w-full">
      <aside className="hidden w-56 shrink-0 flex-col border-r border-sidebar-border bg-sidebar md:flex">
        <div className="flex h-14 items-center gap-2 px-4">
          <span className="flex size-7 items-center justify-center rounded-lg bg-primary/15 text-primary">
            <Sparkles className="size-4" />
          </span>
          <span className="text-sm font-semibold tracking-tight text-sidebar-foreground">
            mcp_videos
          </span>
        </div>

        <nav className="flex flex-1 flex-col gap-1 px-3 py-2">
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={
                  "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors duration-(--duration-fast) " +
                  (active
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground")
                }
              >
                <Icon className="size-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex flex-col gap-2 border-t border-sidebar-border p-3">
          <div className="px-1">
            <p className="truncate text-xs font-medium text-sidebar-foreground">{userName}</p>
            <p className="truncate text-xs text-sidebar-foreground/60">{userEmail}</p>
          </div>
          <form action={logoutAction}>
            <Button type="submit" variant="ghost" size="sm" className="w-full justify-start gap-2">
              <LogOut className="size-3.5" />
              Sair
            </Button>
          </form>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 shrink-0 items-center justify-between border-b border-border bg-background/80 px-4 backdrop-blur-sm md:px-6">
          <div className="flex items-center gap-2 md:hidden">
            <Sparkles className="size-4 text-primary" />
            <span className="text-sm font-semibold">mcp_videos</span>
          </div>
          <p className="hidden text-sm text-muted-foreground md:block">
            {organizationName ?? "Nenhuma organização selecionada"}
          </p>
          <div className="flex items-center gap-1">
            <ThemeToggle />
          </div>
        </header>

        <nav className="flex items-center gap-1 border-b border-border px-2 py-1.5 md:hidden">
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={
                  "flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors " +
                  (active ? "bg-accent text-accent-foreground" : "text-muted-foreground")
                }
              >
                <Icon className="size-3.5" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
