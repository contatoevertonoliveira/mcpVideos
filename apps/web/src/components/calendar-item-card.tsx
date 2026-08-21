import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import type { CalendarItemSummary } from "@/types/channel";

const MOVABLE_STATUSES = new Set(["suggested", "planned", "approved"]);

// Documento 08B sec. 46: a small colored rail on the left represents
// status without painting the whole card - only for items already acted
// on (not suggestions, which use the dashed treatment from sec. 48).
const STATUS_RAIL: Record<string, string> = {
  approved: "border-l-success",
  producing: "border-l-info",
  ready: "border-l-info",
  scheduled: "border-l-info",
  published: "border-l-success",
  cancelled: "border-l-danger",
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

export function CalendarItemCard({
  item,
  channelId,
  approveAction,
  rejectAction,
  rescheduleAction,
  compact = false,
}: {
  item: CalendarItemSummary;
  channelId: string;
  approveAction: (formData: FormData) => void;
  rejectAction: (formData: FormData) => void;
  rescheduleAction?: (formData: FormData) => void;
  compact?: boolean;
}) {
  const isSuggestion = item.status === "suggested" || item.status === "planned";
  const canMove = !compact && rescheduleAction && MOVABLE_STATUSES.has(item.status);
  const time = new Date(item.planned_at).toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div
      className={cn(
        "flex flex-col gap-1.5 rounded-lg p-3 text-xs",
        isSuggestion
          ? "border border-dashed border-border bg-surface"
          : cn("border-l-4 border border-border bg-background", STATUS_RAIL[item.status]),
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="font-medium text-muted-foreground">{time}</span>
        <div className="flex items-center gap-1">
          {isSuggestion && item.source === "ai" && (
            <Badge variant="info" className="px-1.5 text-[10px]">
              IA
            </Badge>
          )}
          <Badge variant="outline" className="px-1.5 text-[10px] uppercase">
            {FORMAT_LABELS[item.content_type] ?? item.content_type}
          </Badge>
        </div>
      </div>
      <p className={cn("font-medium text-foreground", compact && "line-clamp-2")}>
        {item.idea_title ?? "(sem ideia associada)"}
      </p>
      {!isSuggestion && (
        <Badge variant="outline" className="w-fit">
          {STATUS_LABELS[item.status] ?? item.status}
        </Badge>
      )}
      {isSuggestion && (
        <div className="mt-1 flex items-center gap-1.5">
          <form action={approveAction}>
            <input type="hidden" name="channel_id" value={channelId} />
            <input type="hidden" name="item_id" value={item.id} />
            <Button type="submit" size="sm" variant="outline" className="h-7 px-2 text-[11px]">
              Aprovar
            </Button>
          </form>
          <form action={rejectAction}>
            <input type="hidden" name="channel_id" value={channelId} />
            <input type="hidden" name="item_id" value={item.id} />
            <Button type="submit" size="sm" variant="ghost" className="h-7 px-2 text-[11px]">
              Rejeitar
            </Button>
          </form>
        </div>
      )}
      {canMove && (
        <form action={rescheduleAction} className="mt-1 flex items-center gap-1.5">
          <input type="hidden" name="channel_id" value={channelId} />
          <input type="hidden" name="item_id" value={item.id} />
          <Input type="datetime-local" name="planned_at" required className="h-7 w-auto text-[11px]" />
          <Button type="submit" size="sm" variant="outline" className="h-7 px-2 text-[11px]">
            Mover
          </Button>
        </form>
      )}
    </div>
  );
}
