import Link from "next/link";
import { redirect } from "next/navigation";

import { logoutAction } from "@/app/(auth)/actions";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getSessionToken } from "@/lib/session-cookie";
import { getCurrentUser } from "@/services/api/auth";

export default async function DashboardPage() {
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
    <div className="mx-auto flex min-h-svh max-w-3xl flex-col gap-6 p-8">
      <header className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">Organização</p>
          <p className="text-lg font-semibold">
            {activeOrganization?.organization_name ?? "Nenhuma organização selecionada"}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button render={<Link href="/channels" />} variant="outline">
            Canais
          </Button>
          <form action={logoutAction}>
            <Button type="submit" variant="outline">
              Sair
            </Button>
          </form>
        </div>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Bem-vindo(a), {me.user.name}</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">E-mail</span>
            <span>{me.user.email}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Papel na organização</span>
            <Badge variant="secondary">{activeOrganization?.role ?? "-"}</Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Suas organizações</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-2">
          {me.memberships.map((membership) => (
            <div
              key={membership.organization_id}
              className="flex items-center justify-between rounded-md border px-3 py-2 text-sm"
            >
              <span>{membership.organization_name}</span>
              <Badge variant="outline">{membership.role}</Badge>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
