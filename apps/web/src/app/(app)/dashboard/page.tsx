import Link from "next/link";
import { redirect } from "next/navigation";

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
    <div className="mx-auto flex max-w-5xl flex-col gap-8 p-6 md:p-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Bem-vindo(a), {me.user.name}</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          {activeOrganization?.organization_name ?? "Nenhuma organização selecionada"}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-12">
        <Card className="md:col-span-8">
          <CardHeader>
            <CardTitle>Sua conta</CardTitle>
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

        <Card className="md:col-span-4">
          <CardHeader>
            <CardTitle>Canais</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <p className="text-sm text-muted-foreground">
              Conecte um canal do YouTube para começar a produzir conteúdo com IA.
            </p>
            <Button render={<Link href="/channels" />} size="sm">
              Ver canais
            </Button>
          </CardContent>
        </Card>

        <Card className="md:col-span-12">
          <CardHeader>
            <CardTitle>Suas organizações</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-2">
            {me.memberships.map((membership) => (
              <div
                key={membership.organization_id}
                className="flex items-center justify-between rounded-lg border border-border px-3 py-2 text-sm"
              >
                <span>{membership.organization_name}</span>
                <Badge variant="outline">{membership.role}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
