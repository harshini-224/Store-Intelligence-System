"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, HeartPulse, Home, Library, Settings, Upload } from "lucide-react";
import { ThemeToggle } from "@/components/navigation/theme-toggle";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Overview", icon: Home },
  { href: "/upload", label: "Upload", icon: Upload },
  { href: "/videos", label: "Videos", icon: Library },
  { href: "/health", label: "Health", icon: HeartPulse },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen bg-background">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 border-r border-border bg-card/80 p-4 backdrop-blur-xl lg:block">
        <Link href="/" className="flex items-center gap-3 rounded-xl px-2 py-3">
          <span className="rounded-xl bg-primary p-2 text-primary-foreground">
            <Activity className="h-5 w-5" />
          </span>
          <span>
            <span className="block font-semibold">Video Intelligence</span>
            <span className="text-xs text-muted-foreground">Command Center</span>
          </span>
        </Link>
        <nav className="mt-8 space-y-1">
          {navItems.map((item) => {
            const active = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground transition hover:bg-muted hover:text-foreground",
                  active && "bg-primary/10 text-primary"
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 border-b border-border bg-background/80 backdrop-blur-xl">
          <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
            <div>
              <p className="text-sm font-medium">Capability-driven analytics</p>
              <p className="text-xs text-muted-foreground">Works across retail, warehouses, airports, hospitals, and more</p>
            </div>
            <div className="flex items-center gap-2">
              <ThemeToggle />
              <Link
                href="/upload"
                className="inline-flex h-10 items-center justify-center rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90"
              >
                Process Video
              </Link>
            </div>
          </div>
        </header>
        {children}
      </div>
    </div>
  );
}
