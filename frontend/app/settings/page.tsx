"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Monitor, Globe, Code, Bell, CheckCircle } from "lucide-react";
import { useTheme } from "next-themes";

export default function SettingsPage() {
    const { theme, setTheme } = useTheme();
    const [apiUrl, setApiUrl] = useState(
        process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000"
    );
    const [saved, setSaved] = useState(false);

    const handleSave = () => {
        setSaved(true);
        setTimeout(() => setSaved(false), 2500);
    };

    return (
        <div className="page-shell max-w-2xl">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
                <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
                <p className="mt-1 text-muted-foreground">Configure your Video Intelligence Platform preferences.</p>
            </motion.div>

            <div className="space-y-5">
                {/* Appearance */}
                <Section title="Appearance" icon={Monitor}>
                    <div>
                        <Label>Theme</Label>
                        <div className="mt-2 flex gap-2">
                            {(["light", "dark", "system"] as const).map((t) => (
                                <button
                                    key={t}
                                    onClick={() => setTheme(t)}
                                    className={[
                                        "flex-1 rounded-xl border py-2.5 text-sm font-medium capitalize transition",
                                        theme === t
                                            ? "border-primary bg-primary/10 text-primary"
                                            : "border-border bg-muted/40 text-muted-foreground hover:border-primary/50",
                                    ].join(" ")}
                                >
                                    {t}
                                </button>
                            ))}
                        </div>
                    </div>
                </Section>

                {/* API */}
                <Section title="API Configuration" icon={Globe}>
                    <div>
                        <Label>Backend URL</Label>
                        <input
                            type="text"
                            value={apiUrl}
                            onChange={(e) => setApiUrl(e.target.value)}
                            className="mt-2 w-full rounded-xl border border-border bg-muted/40 px-4 py-2.5 text-sm outline-none focus:ring-1 focus:ring-primary"
                            placeholder="http://127.0.0.1:8000"
                        />
                        <p className="mt-1 text-xs text-muted-foreground">
                            Set <code className="rounded bg-muted px-1">NEXT_PUBLIC_API_BASE_URL</code> in your .env.local to persist this.
                        </p>
                    </div>
                </Section>

                {/* Platform Info */}
                <Section title="Platform Info" icon={Code}>
                    <div className="space-y-3 text-sm">
                        <InfoRow label="Frontend" value="Next.js 15 (App Router)" />
                        <InfoRow label="UI Library" value="shadcn/ui + Tailwind CSS" />
                        <InfoRow label="Charts" value="Recharts" />
                        <InfoRow label="Animation" value="Framer Motion" />
                        <InfoRow label="State" value="Zustand + TanStack Query" />
                        <InfoRow label="Backend" value="FastAPI + YOLO + ByteTrack" />
                    </div>
                </Section>

                {/* Notifications */}
                <Section title="Notifications" icon={Bell}>
                    <div className="space-y-3">
                        <Toggle label="Processing completed" defaultChecked />
                        <Toggle label="System health alerts" defaultChecked />
                        <Toggle label="New analytics available" />
                    </div>
                </Section>
            </div>

            <div className="mt-8 flex justify-end">
                <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleSave}
                    className="flex items-center gap-2 rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/20 transition hover:bg-primary/90"
                >
                    {saved ? <><CheckCircle className="h-4 w-4" /> Saved!</> : "Save Changes"}
                </motion.button>
            </div>
        </div>
    );
}

function Section({ title, icon: Icon, children }: { title: string; icon: React.ElementType; children: React.ReactNode }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card rounded-2xl p-6"
        >
            <div className="mb-4 flex items-center gap-2 text-primary">
                <Icon className="h-4 w-4" />
                <h2 className="font-semibold">{title}</h2>
            </div>
            <div className="space-y-4">{children}</div>
        </motion.div>
    );
}

function Label({ children }: { children: React.ReactNode }) {
    return <p className="text-sm font-medium">{children}</p>;
}

function InfoRow({ label, value }: { label: string; value: string }) {
    return (
        <div className="flex items-center justify-between">
            <span className="text-muted-foreground">{label}</span>
            <span className="font-medium">{value}</span>
        </div>
    );
}

function Toggle({ label, defaultChecked = false }: { label: string; defaultChecked?: boolean }) {
    const [checked, setChecked] = useState(defaultChecked);
    return (
        <div className="flex items-center justify-between">
            <p className="text-sm">{label}</p>
            <button
                role="switch"
                aria-checked={checked}
                onClick={() => setChecked(!checked)}
                className={[
                    "relative inline-flex h-5 w-9 items-center rounded-full transition-colors",
                    checked ? "bg-primary" : "bg-muted",
                ].join(" ")}
            >
                <span
                    className={[
                        "inline-block h-3.5 w-3.5 rounded-full bg-white shadow transition-transform",
                        checked ? "translate-x-4" : "translate-x-1",
                    ].join(" ")}
                />
            </button>
        </div>
    );
}
