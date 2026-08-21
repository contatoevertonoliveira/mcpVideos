import { Badge } from "@/components/ui/badge";
import type { CalendarItemSummary } from "@/types/channel";

const STATUS_VARIANT: Record<string, "success" | "info" | "outline" | "destructive"> = {
  published: "success",
  approved: "info",
  scheduled: "info",
  producing: "info",
  ready: "info",
  cancelled: "destructive",
};

const STATUS_LABELS: Record<string, string> = {
  suggested: "Sugestão IA",
  planned: "Planejado",
  approved: "Aprovado",
  producing: "Em produção",
  ready: "Pronto",
  scheduled: "Agendado",
  published: "Publicado",
  cancelled: "Rejeitado",
};

const FORMAT_LABELS: Record<string, string> = {
  short: "Short",
  long_form: "Vídeo",
  live: "Live",
  unknown: "Formato",
};

export function TodayContentItem({ item }: { item: CalendarItemSummary }) {
  const time = new Date(item.planned_at).toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="flex items-center gap-3 rounded-lg border border-border bg-background px-3 py-2.5">
      <span className="w-12 shrink-0 text-sm font-medium text-muted-foreground">{time}</span>
      <Badge variant="outline" className="shrink-0 px-1.5 text-[10px] uppercase">
        {FORMAT_LABELS[item.content_type] ?? item.content_type}
      </Badge>
      <span className="flex-1 truncate text-sm font-medium text-foreground">
        {item.idea_title ?? "(sem ideia associada)"}
      </span>
      <Badge variant={STATUS_VARIANT[item.status] ?? "outline"} className="shrink-0">
        {STATUS_LABELS[item.status] ?? item.status}
      </Badge>
    </div>
  );
}
