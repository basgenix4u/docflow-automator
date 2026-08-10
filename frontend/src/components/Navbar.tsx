"use client";

import React, { useEffect, useState } from "react";
import { ShieldCheck, Cpu, CheckCircle2, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";
import { HealthCheckResponse } from "@/types";

export function Navbar() {
  const [health, setHealth] = useState<HealthCheckResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getHealth()
      .then(data => setHealth(data))
      .catch(err => console.error("Health check error:", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/90 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-50">
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-emerald-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <Cpu className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-slate-100 tracking-tight text-base flex items-center gap-2">
            DocFlow Automator
            <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
              FUW Portal Engine
            </span>
          </h1>
          <p className="text-xs text-slate-400">Enterprise Browser Automation & Document Processing</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {loading ? (
          <span className="text-xs text-slate-500 animate-pulse">Connecting to API Engine...</span>
        ) : health?.status === "online" ? (
          <div className="flex items-center space-x-2 bg-emerald-950/60 border border-emerald-800/80 px-3 py-1.5 rounded-full text-xs font-mono text-emerald-400">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>PLAYWRIGHT ENGINE ONLINE</span>
          </div>
        ) : (
          <div className="flex items-center space-x-2 bg-rose-950/60 border border-rose-800/80 px-3 py-1.5 rounded-full text-xs font-mono text-rose-400">
            <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
            <span>ENGINE DISCONNECTED</span>
          </div>
        )}

        <div className="border-l border-slate-800 h-6 mx-1" />

        <div className="flex items-center space-x-2 text-xs text-slate-300 bg-slate-800/60 px-3 py-1.5 rounded-md border border-slate-700">
          <ShieldCheck className="w-4 h-4 text-cyan-400" />
          <span>Demo User: <strong className="text-slate-100 font-mono">BSC/BCH/24/140</strong></span>
        </div>
      </div>
    </header>
  );
}
