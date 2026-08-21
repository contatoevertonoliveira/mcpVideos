import { ChevronLeft, ChevronRight } from "lucide-react";
import Link from "next/link";

import { cn } from "@/lib/utils";

export function CalendarToolbar({
  basePath,
  view,
  weekLabel,
  prevWeekHref,
  nextWeekHref,
}: {
  basePath: string;
  view: "week" | "list";
  weekLabel: string;
  prevWeekHref: string;
  nextWeekHref: string;
}) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div className="flex items-center gap-2">
        {view === "week" && (
          <>
            <Link
              href={prevWeekHref}
              className="rounded-md border border-border p-1.5 text-muted-foreground hover:text-foreground"
            >
              <ChevronLeft className="size-4" />
            </Link>
            <span className="text-sm font-medium text-foreground">{weekLabel}</span>
            <Link
              href={nextWeekHref}
              className="rounded-md border border-border p-1.5 text-muted-foreground hover:text-foreground"
            >
              <ChevronRight className="size-4" />
            </Link>
          </>
        )}
      </div>
      <div className="flex gap-1 rounded-lg border border-border p-1">
        <Link
          href={`${basePath}?view=week`}
          className={cn(
            "rounded-md px-3 py-1 text-xs font-medium",
            view === "week" ? "bg-secondary text-secondary-foreground" : "text-muted-foreground",
          )}
        >
          Semana
        </Link>
        <Link
          href={`${basePath}?view=list`}
          className={cn(
            "rounded-md px-3 py-1 text-xs font-medium",
            view === "list" ? "bg-secondary text-secondary-foreground" : "text-muted-foreground",
          )}
        >
          Lista
        </Link>
      </div>
    </div>
  );
}
