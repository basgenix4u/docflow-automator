"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Cpu, RefreshCw, UserPlus } from "lucide-react";
import { api } from "@/lib/api";
import { setSession } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.register({ email, full_name: fullName, password });
      const res = await api.login({ email, password });
      setSession(res.access_token, res.user);
      router.replace("/portals");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Registration failed";
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
            <h1 className="text-lg font-bold text-white">Create operator account</h1>
            <p className="text-xs text-emerald-200/70">Self-registration is limited to ENGINEER role</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4" aria-label="Operator registration">
          <div className="space-y-1.5">
            <label htmlFor="full_name" className="text-xs font-semibold text-emerald-200">
              Full name
            </label>
            <input
              id="full_name"
              type="text"
              required
              minLength={2}
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full bg-emerald-900/40 border border-emerald-700/80 rounded-xl p-3 text-white text-sm focus:outline-none focus:border-emerald-400"
            />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="email" className="text-xs font-semibold text-emerald-200">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-emerald-900/40 border border-emerald-700/80 rounded-xl p-3 text-white text-sm focus:outline-none focus:border-emerald-400"
            />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="password" className="text-xs font-semibold text-emerald-200">
              Password (min 8 characters)
            </label>
            <input
              id="password"
              type="password"
              required
              minLength={8}
              autoComplete="new-password"
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
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <UserPlus className="w-4 h-4" />}
            <span>{loading ? "Creating account..." : "Create account"}</span>
          </button>
        </form>

        <p className="text-xs text-emerald-200/70 text-center">
          Already registered?{" "}
          <Link href="/login" className="text-emerald-300 underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
