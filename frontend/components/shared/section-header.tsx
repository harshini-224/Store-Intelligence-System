export function SectionHeader({
  eyebrow,
  title,
  description,
  subtitle,
  icon: Icon,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  subtitle?: string;
  icon?: React.ElementType;
}) {
  return (
    <div>
      {eyebrow ? (
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-primary">{eyebrow}</p>
      ) : null}
      <div className="flex items-center gap-2">
        {Icon && <Icon className="h-4 w-4 text-primary" />}
        <h2 className="font-semibold tracking-tight">{title}</h2>
      </div>
      {(subtitle || description) ? (
        <p className="mt-0.5 text-xs text-muted-foreground">{subtitle ?? description}</p>
      ) : null}
    </div>
  );
}
