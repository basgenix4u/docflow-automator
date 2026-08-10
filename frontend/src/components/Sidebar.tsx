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
  Terminal
} from "lucide-react";

const navigation = [
  { name: "Command Center", href: "/dashboard", icon: LayoutDashboard },
  { name: "Target Portals", href: "/portals", icon: Globe2 },
  { name: "Workflows & Runner", href: "/workflows", icon: Workflow },
  { name: "Document Studio (PDF)", href: "/documents", icon: FileText },
  { name: "Security Audit Scanner", href: "/security", icon: ShieldAlert },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between p-4 shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="space-y-6">
        <div className="px-2">
          <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider font-mono">
            Navigation Core
          </p>
        </div>

        <nav className="space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href || (pathname === "/" && item.href === "/dashboard");
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? "bg-cyan-600/20 text-cyan-300 border border-cyan-500/30 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-cyan-400" : "text-slate-500"}`} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="bg-slate-950/80 border border-slate-800/80 rounded-xl p-3.5 space-y-2 text-xs">
        <div className="flex items-center space-x-2 text-slate-300 font-semibold">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <span>Active Target Portal</span>
        </div>
        <p className="text-slate-400 truncate font-mono text-[11px]">
          ug.fuwportal.edu.ng
        </p>
        <div className="pt-1 flex items-center justify-between text-[11px] text-slate-500 border-t border-slate-900">
          <span>Engine: Playwright</span>
          <span className="text-emerald-400 font-medium">Ready</span>
        </div>
      </div>
    </aside>
  );
}
