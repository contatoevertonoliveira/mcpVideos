import { CalendarItemCard } from "@/components/calendar-item-card";
import type { CalendarItemSummary } from "@/types/channel";

const DAY_LABELS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"];

export function EditorialCalendar({
  weekStart,
  items,
  channelId,
  approveAction,
  rejectAction,
}: {
  weekStart: Date;
  items: CalendarItemSummary[];
  channelId: string;
  approveAction: (formData: FormData) => void;
  rejectAction: (formData: FormData) => void;
}) {
  const days = Array.from({ length: 7 }, (_, index) => {
    const date = new Date(weekStart);
    date.setDate(date.getDate() + index);
    return date;
  });

  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-7">
      {days.map((day, index) => {
        const dayItems = items.filter((item) => {
          const planned = new Date(item.planned_at);
          return (
            planned.getFullYear() === day.getFullYear() &&
            planned.getMonth() === day.getMonth() &&
            planned.getDate() === day.getDate()
          );
        });
        const isToday = new Date().toDateString() === day.toDateString();

        return (
          <div key={day.toISOString()} className="flex flex-col gap-2">
            <div
              className={
                "rounded-lg border px-2 py-1.5 text-center text-xs font-medium " +
                (isToday
                  ? "border-primary/40 bg-primary/10 text-primary"
                  : "border-border text-muted-foreground")
              }
            >
              {DAY_LABELS[index]} · {day.getDate()}/{day.getMonth() + 1}
            </div>
            <div className="flex flex-col gap-2">
              {dayItems.length === 0 ? (
                <p className="rounded-lg border border-dashed border-border/60 px-2 py-3 text-center text-[11px] text-muted-foreground">
                  Sem itens
                </p>
              ) : (
                dayItems.map((item) => (
                  <CalendarItemCard
                    key={item.id}
                    item={item}
                    channelId={channelId}
                    approveAction={approveAction}
                    rejectAction={rejectAction}
                    compact
                  />
                ))
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
