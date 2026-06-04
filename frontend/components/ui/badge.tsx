import * as React from "react";
import { cn } from "@/lib/utils";

type BadgeProps = React.HTMLAttributes<HTMLSpanElement> & {
  tone?: "default" | "success" | "warning" | "danger";
};

export function Badge({ className, tone = "default", ...props }: BadgeProps) {
  const tones = {
    default: "border-border bg-muted text-muted-foreground",
    success: "border-teal-400/30 bg-teal-400/10 text-teal-500 dark:text-teal-200",
    warning: "border-amber-400/30 bg-amber-400/10 text-amber-600 dark:text-amber-200",
    danger: "border-rose-400/30 bg-rose-400/10 text-rose-600 dark:text-rose-200",
  };
  return (
    <span
      className={cn("inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium", tones[tone], className)}
      {...props}
    />
  );
}
