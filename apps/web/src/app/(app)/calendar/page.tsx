import { CalendarItemCard } from "@/components/calendar-item-card";
import { CalendarToolbar } from "@/components/calendar-toolbar";
import { EditorialCalendar } from "@/components/editorial-calendar";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { getSessionToken } from "@/lib/session-cookie";
import { listChannelCalendar, listChannels } from "@/services/api/channels";

import {
  approveCalendarItemAction,
  rejectCalendarItemAction,
  rescheduleCalendarItemAction,
  triggerCalendarGenerationAction,
} from "../channels/actions";

function mondayOf(date: Date): Date {
  const monday = new Date(date);
  const day = monday.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  monday.setDate(monday.getDate() + diff);
  monday.setHours(0, 0, 0, 0);
  return monday;
}

function formatWeekLabel(weekStart: Date): string {
  const weekEnd = new Date(weekStart);
  weekEnd.setDate(weekEnd.getDate() + 6);
  const fmt = (date: Date) => date.toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
  return `${fmt(weekStart)} – ${fmt(weekEnd)}`;
}

function toParam(date: Date): string {
  return date.toISOString().slice(0, 10);
}

export default async function CalendarPage(props: PageProps<"/calendar">) {
  const token = await getSessionToken();
  if (!token) {
    return null;
  }

  const searchParams = await props.searchParams;
  const view = searchParams.view === "list" ? "list" : "week";
  const weekParam = typeof searchParams.week === "string" ? searchParams.week : null;
  const parsedWeek = weekParam ? new Date(weekParam) : new Date();
  const weekStart = mondayOf(Number.isNaN(parsedWeek.getTime()) ? new Date() : parsedWeek);

  const channels = await listChannels(token);
  const channel = channels.find((item) => item.connection_status === "connected") ?? channels[0];

  if (!channel) {
    return (
      <div className="mx-auto flex max-w-5xl flex-col gap-6 p-6 md:p-8">
        <PageHeader title="Calendário" subtitle="Planeje o que será produzido e publicado." />
        <Card>
          <CardContent className="py-10 text-center text-sm text-muted-foreground">
            Conecte um canal em <a href="/channels" className="underline">Canais</a> para começar a
            planejar o calendário.
          </CardContent>
        </Card>
      </div>
    );
  }

  const items = await listChannelCalendar(token, channel.id);

  const prevWeek = new Date(weekStart);
  prevWeek.setDate(prevWeek.getDate() - 7);
  const nextWeek = new Date(weekStart);
  nextWeek.setDate(nextWeek.getDate() + 7);

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6 p-6 md:p-8">
      <PageHeader
        title="Calendário"
        subtitle={`${items.length} item(ns) no calendário de ${channel.name}.`}
        action={
          <form action={triggerCalendarGenerationAction}>
            <input type="hidden" name="channel_id" value={channel.id} />
            <Button type="submit">Gerar calendário</Button>
          </form>
        }
      />

      <CalendarToolbar
        basePath="/calendar"
        view={view}
        weekLabel={formatWeekLabel(weekStart)}
        prevWeekHref={`/calendar?view=week&week=${toParam(prevWeek)}`}
        nextWeekHref={`/calendar?view=week&week=${toParam(nextWeek)}`}
      />

      {items.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-sm text-muted-foreground">
            Nenhum item no calendário ainda. Aprove uma ideia em{" "}
            <a href="/ideas" className="underline">
              Ideias
            </a>{" "}
            e clique em &ldquo;Gerar calendário&rdquo;.
          </CardContent>
        </Card>
      ) : view === "week" ? (
        <EditorialCalendar
          weekStart={weekStart}
          items={items}
          channelId={channel.id}
          approveAction={approveCalendarItemAction}
          rejectAction={rejectCalendarItemAction}
        />
      ) : (
        <div className="flex flex-col gap-2">
          {items.map((item) => (
            <CalendarItemCard
              key={item.id}
              item={item}
              channelId={channel.id}
              approveAction={approveCalendarItemAction}
              rejectAction={rejectCalendarItemAction}
              rescheduleAction={rescheduleCalendarItemAction}
            />
          ))}
        </div>
      )}
    </div>
  );
}
