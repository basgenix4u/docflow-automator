"use client";

import React, { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Cpu, LogIn, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
import { setSession } from "@/lib/auth";

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen" />}>
      <LoginForm />
    </Suspense>
  );
}

function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const nextPath = params.get("next") || "/portals";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await api.login({ email, password });
      setSession(res.access_token, res.user);
      router.replace(nextPath);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Login failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-emerald-950/80 border border-emerald-800 rounded-2xl p-8 space-y-6 shadow-2xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-emerald-600 to-green-400 flex items-center justify-center">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">Operator sign in</h1>
            <p className="text-xs text-emerald-200/70">DocFlow Automator command center</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4" aria-label="Operator login">
          <div className="space-y-1.5">
            <label htmlFor="email" className="text-xs font-semibold text-emerald-200">
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-emerald-900/40 border border-emerald-700/80 rounded-xl p-3 text-white text-sm focus:outline-none focus:border-emerald-400"
            />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="password" className="text-xs font-semibold text-emerald-200">
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-emerald-900/40 border border-emerald-700/80 rounded-xl p-3 text-white text-sm focus:outline-none focus:border-emerald-400"
            />
          </div>

          {error && (
            <p role="alert" className="text-xs text-rose-300 bg-rose-950/50 border border-rose-800 rounded-lg p-3">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full px-4 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <LogIn className="w-4 h-4" />}
            <span>{loading ? "Signing in..." : "Sign in"}</span>
          </button>
        </form>

        <p className="text-xs text-emerald-200/70 text-center">
          Need an operator account?{" "}
          <Link href="/register" className="text-emerald-300 underline">
            Register
          </Link>
          {" · "}
          <Link href="/" className="text-emerald-300 underline">
            Student printer
          </Link>
        </p>
      </div>
    </div>
  );
}
