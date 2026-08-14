import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "@/components/AppShell";

export const metadata: Metadata = {
  title: "DocFlow Automator — FUW Portal Automation & Security Platform",
  description:
    "Enterprise multi-user browser workflow orchestration, document extraction, A4/A5 PDF generation, and portal authentication security testing.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 min-h-screen flex flex-col font-sans antialiased selection:bg-cyan-500/30 selection:text-cyan-200">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
