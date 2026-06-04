import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "@/components/navigation/app-shell";
import { Providers } from "@/app/providers";

export const metadata: Metadata = {
  title: "Video Intelligence Platform",
  description: "Capability-driven video analytics frontend for processed intelligence artifacts.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers>
          <AppShell>{children}</AppShell>
        </Providers>
      </body>
    </html>
  );
}
