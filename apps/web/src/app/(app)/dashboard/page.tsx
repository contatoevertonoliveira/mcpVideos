import Link from "next/link";
import { redirect } from "next/navigation";

import { MetricCard } from "@/components/metric-card";
import { PageHeader } from "@/components/page-header";
import { TodayContentItem } from "@/components/today-content-item";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getSessionToken } from "@/lib/session-cookie";
import { getCurrentUser } from "@/services/api/auth";
import {
  getChannelDNA,
  getChannelStrategyStatus,
  listChannelCalendar,
  listChannelIdeas,
  listChannels,
  listChannelVideos,
} from "@/services/api/channels";

const AUTOMATION_LABELS: Record<string, string> = {
  manual: "Manual",
  assisted: "Assistido",
  semi_auto: "Semi-automático",
  autopilot: "Autopilot",
};

function greeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "Bom dia";
  if (hour < 18) return "Boa tarde";
  return "Boa noite";
}

function isToday(isoDate: string): boolean {
  const date = new Date(isoDate);
  const now = new Date();
  return (
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate()
  );
}

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

  const channels = await listChannels(token);
  const channel = channels.find((item) => item.connection_status === "connected") ?? channels[0];

  if (!channel) {
    return (
      <div className="mx-auto flex max-w-5xl flex-col gap-6 p-6 md:p-8">
        <PageHeader
          title={`${greeting()}, ${me.user.name}`}
          subtitle={activeOrganization?.organization_name ?? "Nenhuma organização selecionada"}
        />
        <Card>
          <CardContent className="flex flex-col items-center gap-3 py-10 text-center text-sm text-muted-foreground">
            <p>Conecte um canal do YouTube para começar a produzir conteúdo com IA.</p>
            <Button render={<Link href="/channels" />} size="sm">
              Conectar canal
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const [videos, dna, strategy, ideas, calendar] = await Promise.all([
    listChannelVideos(token, channel.id),
    getChannelDNA(token, channel.id),
    getChannelStrategyStatus(token, channel.id),
    listChannelIdeas(token, channel.id),
    listChannelCalendar(token, channel.id),
  ]);

  const todayItems = calendar.filter((item) => isToday(item.planned_at));
  const suggestedCount = calendar.filter((item) => item.status === "suggested").length;
  const approvedIdeasCount = ideas.filter((idea) => idea.status === "approved").length;

  const attentionItems: { label: string; href: string }[] = [];
  if (strategy.pending_draft) {
    attentionItems.push({ label: "Nova estratégia aguardando aprovação", href: "/channels" });
  }
  if (suggestedCount > 0) {
    attentionItems.push({
      label: `${suggestedCount} sugestão(ões) de calendário aguardando revisão`,
      href: "/calendar",
    });
  }

  const statusChecks = [
    { label: "Canal conectado", ok: channel.connection_status === "connected" },
    { label: "DNA do canal ativo", ok: dna !== null },
    { label: "Estratégia ativa", ok: strategy.active !== null },
    { label: "Calendário com itens", ok: calendar.length > 0 },
  ];

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6 p-6 md:p-8">
      <PageHeader
        title={`${greeting()}, ${me.user.name}`}
        subtitle={
          todayItems.length > 0
            ? `${channel.name} · ${todayItems.length} item(ns) programado(s) para hoje.`
            : `${channel.name} · Nada programado para hoje.`
        }
        action={
          <Badge variant="info">{AUTOMATION_LABELS[channel.automation_mode] ?? channel.automation_mode}</Badge>
        }
      />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-12">
        <Card className="md:col-span-8">
          <CardHeader>
            <CardTitle>Hoje</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-2">
            {todayItems.length === 0 ? (
              <p className="py-6 text-center text-sm text-muted-foreground">
                Nada agendado para hoje.
              </p>
            ) : (
              todayItems.map((item) => <TodayContentItem key={item.id} item={item} />)
            )}
          </CardContent>
        </Card>

        <div className="flex flex-col gap-4 md:col-span-4">
          <Card>
            <CardHeader>
              <CardTitle>Status operacional</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-2 text-sm">
              {statusChecks.map((check) => (
                <div key={check.label} className="flex items-center gap-1.5">
                  <span className={check.ok ? "text-success" : "text-muted-foreground"}>
                    {check.ok ? "✓" : "○"}
                  </span>
                  <span className="text-muted-foreground">{check.label}</span>
                </div>
              ))}
            </CardContent>
          </Card>

          {attentionItems.length > 0 && (
            <Card className="border-warning/40 bg-warning/10">
              <CardHeader>
                <CardTitle className="text-warning">Precisa da sua atenção</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col gap-2">
                {attentionItems.map((item) => (
                  <Link
                    key={item.label}
                    href={item.href}
                    className="text-sm font-medium text-foreground underline-offset-2 hover:underline"
                  >
                    {item.label}
                  </Link>
                ))}
              </CardContent>
            </Card>
          )}
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 md:col-span-12">
          <MetricCard label="Vídeos importados" value={String(videos.length)} />
          <MetricCard label="Ideias aprovadas" value={String(approvedIdeasCount)} />
          <MetricCard label="Itens no calendário" value={String(calendar.length)} />
        </div>
      </div>
    </div>
  );
}
