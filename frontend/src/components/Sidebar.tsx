"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Globe2,
  Workflow,
  FileText,
  ShieldAlert,
  Printer
} from "lucide-react";

const navigation = [
  { name: "Command Center", href: "/dashboard", icon: LayoutDashboard },
  { name: "Target Portals", href: "/portals", icon: Globe2 },
  { name: "Workflows & Orchestrator", href: "/workflows", icon: Workflow },
  { name: "Document Studio (A4/A5)", href: "/documents", icon: FileText },
  { name: "Security Audit Scanner", href: "/security", icon: ShieldAlert },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-emerald-950/90 border-r border-emerald-800/60 flex flex-col justify-between p-4 shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="space-y-6">
        <div className="px-2">
          <p className="text-[11px] font-bold text-emerald-300 uppercase tracking-wider font-mono">
            Navigation Core
          </p>
        </div>

        <nav className="space-y-1.5">
          {navigation.map((item) => {
            const isActive = pathname === item.href || (pathname === "/" && item.href === "/dashboard");
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? "bg-emerald-600/30 text-emerald-200 border border-emerald-500/40 shadow-sm shadow-emerald-500/10"
                    : "text-emerald-100/70 hover:text-white hover:bg-emerald-900/40"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-emerald-400" : "text-emerald-300/50"}`} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="bg-emerald-900/40 border border-emerald-800/80 rounded-xl p-3.5 space-y-2 text-xs">
        <div className="flex items-center space-x-2 text-emerald-200 font-semibold">
          <Printer className="w-4 h-4 text-emerald-400" />
          <span>Universal Document Printer</span>
        </div>
        <p className="text-emerald-300/70 truncate font-mono text-[11px]">
          Dynamic Portal Webview Captures
        </p>
        <div className="pt-1.5 flex items-center justify-between text-[11px] text-emerald-300/50 border-t border-emerald-800/60">
          <span>Engine: Playwright</span>
          <span className="text-emerald-400 font-bold">Active</span>
        </div>
      </div>
    </aside>
  );
}
