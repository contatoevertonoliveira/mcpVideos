import Link from "next/link";

import { cn } from "@/lib/utils";

export interface FilterChipOption {
  label: string;
  value: string;
}

export function FilterChips({
  basePath,
  paramName,
  options,
  activeValue,
}: {
  basePath: string;
  paramName: string;
  options: FilterChipOption[];
  activeValue: string;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((option) => {
        const active = option.value === activeValue;
        const href =
          option.value === "all" ? basePath : `${basePath}?${paramName}=${option.value}`;
        return (
          <Link
            key={option.value}
            href={href}
            className={cn(
              "rounded-full border px-3 py-1.5 text-xs font-medium transition-colors",
              active
                ? "border-transparent bg-secondary text-secondary-foreground"
                : "border-border text-muted-foreground hover:text-foreground",
            )}
          >
            {option.label}
          </Link>
        );
      })}
    </div>
  );
}
