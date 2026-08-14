"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { ShieldCheck, Cpu, CheckCircle2, AlertCircle, LogIn, LogOut } from "lucide-react";
import { api } from "@/lib/api";
import { HealthCheckResponse, User } from "@/types";
import { clearSession, getStoredUser } from "@/lib/auth";

export function Navbar() {
  const [health, setHealth] = useState<HealthCheckResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    setUser(getStoredUser());
    api.getHealth()
      .then((data) => setHealth(data))
      .catch((err) => console.error("Health check error:", err))
      .finally(() => setLoading(false));
  }, []);

  const handleLogout = () => {
    clearSession();
    setUser(null);
    window.location.href = "/";
  };

  return (
    <header className="h-16 border-b border-emerald-800/60 bg-emerald-950/90 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-50">
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-emerald-600 to-green-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
          <Cpu className="w-5 h-5 text-white" aria-hidden="true" />
        </div>
        <div>
          <h1 className="font-bold text-white tracking-tight text-base flex items-center gap-2">
            DocFlow Automator
            <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-900/80 text-emerald-300 border border-emerald-700">
              Multi-Portal Engine
            </span>
          </h1>
          <p className="text-xs text-emerald-200/70">Autonomous Webview Interception & 1-Page PDF Generator</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {loading ? (
          <span className="text-xs text-emerald-300/60 animate-pulse font-mono">Connecting to Engine...</span>
        ) : health?.status === "online" ? (
          <div className="flex items-center space-x-2 bg-emerald-900/60 border border-emerald-700/80 px-3.5 py-1.5 rounded-full text-xs font-mono text-emerald-300">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" aria-hidden="true" />
            <span>PLAYWRIGHT ENGINE ONLINE</span>
          </div>
        ) : (
          <div className="flex items-center space-x-2 bg-rose-950/80 border border-rose-800/80 px-3.5 py-1.5 rounded-full text-xs font-mono text-rose-300">
            <AlertCircle className="w-3.5 h-3.5 text-rose-400" aria-hidden="true" />
            <span>ENGINE DISCONNECTED</span>
          </div>
        )}

        <div className="border-l border-emerald-800/60 h-6 mx-1" />

        <div className="hidden md:flex items-center space-x-2 text-xs text-emerald-100 bg-emerald-900/40 px-3 py-1.5 rounded-md border border-emerald-800">
          <ShieldCheck className="w-4 h-4 text-emerald-400" aria-hidden="true" />
          <span className="font-mono">Operator APIs protected</span>
        </div>

        {user ? (
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-xs font-mono text-emerald-100 bg-emerald-900/40 px-3 py-1.5 rounded-md border border-emerald-800 hover:bg-emerald-800/60"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>{user.full_name}</span>
          </button>
        ) : (
          <Link
            href="/login"
            className="flex items-center gap-2 text-xs font-mono text-slate-950 bg-emerald-400 px-3 py-1.5 rounded-md font-bold"
          >
            <LogIn className="w-3.5 h-3.5" />
            <span>Operator login</span>
          </Link>
        )}
      </div>
    </header>
  );
}
