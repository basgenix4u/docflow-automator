"use client";

import React, { useEffect, useState } from "react";
import { Globe2, ShieldCheck, Plus, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
import { Portal } from "@/types";

export default function PortalsPage() {
  const [portals, setPortals] = useState<Portal[]>([]);
  const [loading, setLoading] = useState(true);
  const [testingId, setTestingId] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<Record<string, unknown> | null>(null);

  // New Portal Modal state
  const [showModal, setShowModal] = useState(false);
  const [newName, setNewName] = useState("");
  const [newUrl, setNewUrl] = useState("");
  const [newDemoUser, setNewDemoUser] = useState("");
  const [newDemoPass, setNewDemoPass] = useState("");

  const loadPortals = async () => {
    setLoading(true);
    try {
      const data = await api.getPortals();
      setPortals(data);
    } catch (err) {
      console.error("Portals load error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPortals();
  }, []);

  const handleTestAuth = async (portalId: string) => {
    setTestingId(portalId);
    setTestResult(null);
    try {
      const res = await api.testPortalAuth(portalId);
      setTestResult(res);
    } catch (err: unknown) {
      console.error("Auth test error:", err);
      setTestResult({ error: err instanceof Error ? err.message : "Auth test failed" });
    } finally {
      setTestingId(null);
    }
  };

  const handleCreatePortal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName || !newUrl) return;
    try {
      await api.createPortal({
        name: newName,
        base_url: newUrl,
        demo_username: newDemoUser,
        demo_password: newDemoPass,
      });
      setShowModal(false);
      setNewName("");
      setNewUrl("");
      setNewDemoUser("");
      setNewDemoPass("");
      await loadPortals();
    } catch (err) {
      console.error("Create portal error:", err);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <Globe2 className="w-6 h-6 text-cyan-400" />
            <span>Target Portals Registry</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Registered web portals for automated browser orchestration and security testing.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition-all flex items-center gap-2 shadow-lg shadow-cyan-600/20"
        >
          <Plus className="w-4 h-4" />
          <span>Register New Portal</span>
        </button>
      </div>

      {testResult && (
        <div className={`p-4 rounded-xl border text-xs font-mono space-y-2 ${
          testResult.error
            ? "bg-rose-950/40 border-rose-800 text-rose-300"
            : "bg-emerald-950/40 border-emerald-800 text-emerald-300"
        }`}>
          <div className="flex items-center justify-between font-bold">
            <span>Portal Security Audit Results: {String(testResult.portal_name || "Target Portal")}</span>
            <button onClick={() => setTestResult(null)} className="text-slate-400 hover:text-slate-200">Close</button>
          </div>
          {testResult.error ? (
            <p>Error: {String(testResult.error)}</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-slate-300">
              <div>Target URL: <span className="text-white">{String(testResult.url || "")}</span></div>
              <div>Security Score: <span className="text-emerald-400 font-bold">{String(testResult.security_score ?? 0)}/100</span></div>
              <div>Vulnerabilities: <span className="text-amber-400 font-bold">{Array.isArray(testResult.vulnerabilities) ? testResult.vulnerabilities.length : Number(testResult.vulnerabilities || 0)}</span></div>
            </div>
          )}
        </div>
      )}

      {loading ? (
        <div className="text-center py-12 text-slate-500 text-xs font-mono animate-pulse">
          Loading target portals registry...
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {portals.map((portal) => (
            <div key={portal.id} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-6">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
                <div className="space-y-1">
                  <div className="flex items-center space-x-3">
                    <h2 className="text-lg font-bold text-white">{portal.name}</h2>
                    <span className="px-2.5 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px] font-mono uppercase">
                      {portal.status}
                    </span>
                  </div>
                  <p className="text-xs text-cyan-400 font-mono">{portal.base_url}</p>
                </div>

                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => handleTestAuth(portal.id)}
                    disabled={testingId === portal.id}
                    className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-700 transition-all flex items-center gap-2"
                  >
                    {testingId === portal.id ? (
                      <>
                        <RefreshCw className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                        <span>Testing Security...</span>
                      </>
                    ) : (
                      <>
                        <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                        <span>Run Security Audit</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs font-mono">
                <div className="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800 space-y-1">
                  <span className="text-slate-500 text-[11px] block">AUTH TYPE</span>
                  <span className="text-slate-200 font-bold">{portal.auth_type} FORM</span>
                </div>
                <div className="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800 space-y-1">
                  <span className="text-slate-500 text-[11px] block">USERNAME SELECTOR</span>
                  <span className="text-slate-200 font-bold">#{portal.username_field}</span>
                </div>
                <div className="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800 space-y-1">
                  <span className="text-slate-500 text-[11px] block">DEMO USERNAME</span>
                  <span className="text-cyan-400 font-bold">{portal.demo_username || "N/A"}</span>
                </div>
                <div className="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800 space-y-1">
                  <span className="text-slate-500 text-[11px] block">DEMO PASSWORD</span>
                  <span className="text-slate-200">••••••••</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal for Registering Portal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 space-y-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h3 className="text-base font-bold text-white">Register Target Portal</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-200 text-xs">Close</button>
            </div>

            <form onSubmit={handleCreatePortal} className="space-y-4 text-xs font-mono">
              <div className="space-y-1.5">
                <label className="text-slate-300 block font-sans">Portal Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Federal University Portal"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-slate-300 block font-sans">Base URL</label>
                <input
                  type="url"
                  required
                  placeholder="https://ug.fuwportal.edu.ng/index.php"
                  value={newUrl}
                  onChange={(e) => setNewUrl(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-slate-300 block font-sans">Demo Username</label>
                  <input
                    type="text"
                    placeholder="Student User ID"
                    value={newDemoUser}
                    onChange={(e) => setNewDemoUser(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-100 focus:outline-none focus:border-cyan-500"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-slate-300 block font-sans">Demo Password</label>
                  <input
                    type="password"
                    placeholder="Omotola"
                    value={newDemoPass}
                    onChange={(e) => setNewDemoPass(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-100 focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-sans text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-sans text-xs font-semibold"
                >
                  Save Portal
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
