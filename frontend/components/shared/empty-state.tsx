import { Inbox } from "lucide-react";

export function EmptyState({ title, message }: { title?: string; message: string }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-border bg-muted/30 py-12 text-center">
      <Inbox className="h-10 w-10 text-muted-foreground/40" />
      {title && <h3 className="mt-4 font-semibold">{title}</h3>}
      <p className="mt-2 max-w-md text-sm text-muted-foreground">{message}</p>
    </div>
  );
}
