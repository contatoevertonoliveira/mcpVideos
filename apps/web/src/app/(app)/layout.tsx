import { redirect } from "next/navigation";
import type { ReactNode } from "react";

import { logoutAction } from "@/app/(auth)/actions";
import { AppShell } from "@/components/app-shell";
import { getSessionToken } from "@/lib/session-cookie";
import { getCurrentUser } from "@/services/api/auth";

export default async function AppLayout({ children }: { children: ReactNode }) {
  const token = await getSessionToken();
  if (!token) {
    redirect("/login");
  }

  const me = await getCurrentUser(token);
  if (!me) {
    redirect("/login");
  }

  const activeOrganization = me.memberships.find(
    (m) => m.organization_id === me.active_organization_id,
  );

  return (
    <AppShell
      userName={me.user.name}
      userEmail={me.user.email}
      organizationName={activeOrganization?.organization_name ?? null}
      logoutAction={logoutAction}
    >
      {children}
    </AppShell>
  );
}
