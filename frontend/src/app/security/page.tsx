"use client";

import React, { useEffect, useState } from "react";
import { ShieldAlert, ShieldCheck, Play, AlertTriangle, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
import { Portal, SecurityScan, SecurityTest, Vulnerability } from "@/types";

export default function SecurityPage() {
  const [portals, setPortals] = useState<Portal[]>([]);
  const [scans, setScans] = useState<SecurityScan[]>([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [activeScan, setActiveScan] = useState<SecurityScan | null>(null);

  const loadSecurityData = async () => {
    setLoading(true);
    try {
      const [pData, sData] = await Promise.all([
        api.getPortals(),
        api.getSecurityScans(),
      ]);
      setPortals(pData);
      setScans(sData);
      if (sData.length > 0 && !activeScan) {
        setActiveScan(sData[0]);
      }
    } catch (err) {
      console.error("Security data load error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadSecurityData();
    // Initial operator console load only.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleRunSecurityScan = async (portalId: string) => {
    setScanning(true);
    try {
      const scan = await api.triggerSecurityScan(portalId);
      setActiveScan(scan);
      await loadSecurityData();
    } catch (err) {
      console.error("Run scan error:", err);
    } finally {
      setScanning(false);
    }
  };

  const fuwPortal = portals.find(p => p.base_url.includes("fuwportal")) || portals[0];

  const reportData = activeScan ? JSON.parse(activeRunReport(activeScan)) : null;
  const testsList: SecurityTest[] = reportData?.tests || [];
  const vulnsList: Vulnerability[] = reportData?.vulnerabilities || [];

  function activeRunReport(scan: SecurityScan) {
    try {
      return scan.report_json || "{}";
    } catch {
      return "{}";
    }
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <ShieldAlert className="w-6 h-6 text-amber-400" />
            <span>Portal Authentication Security Testing Core</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Automated security controls evaluation for HTTP headers, CSRF enforcement, session token freshness, and transport encryption.
          </p>
        </div>

        {fuwPortal && (
          <button
            onClick={() => handleRunSecurityScan(fuwPortal.id)}
            disabled={scanning}
            className="px-4 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-slate-950 font-bold text-xs transition-all flex items-center gap-2 shadow-lg shadow-amber-600/20 disabled:opacity-50"
          >
            {scanning ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin text-slate-950" />
                <span>Auditing ug.fuwportal.edu.ng...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-slate-950 text-slate-950" />
                <span>Run FUW Portal Security Audit</span>
              </>
            )}
          </button>
        )}
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-500 text-xs font-mono animate-pulse">
          Loading security audit reports...
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Col: Security Score Card & Vulnerabilities */}
          <div className="space-y-6">
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4 text-center">
              <span className="text-xs font-mono text-slate-400 block uppercase">Overall Security Compliance Score</span>
              <div className="text-5xl font-black text-amber-400 tracking-tight font-mono">
                {activeScan ? activeScan.score : 78}<span className="text-2xl text-slate-500">/100</span>
              </div>
              <p className="text-xs text-slate-400">
                Target: {fuwPortal?.base_url || "ug.fuwportal.edu.ng"} · {scans.length} stored scans
              </p>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>Identified Security Gaps ({vulnsList.length})</span>
              </h3>

              {vulnsList.length === 0 ? (
                <div className="text-xs text-emerald-400 font-mono py-4 text-center">
                  No critical vulnerabilities detected in last audit.
                </div>
              ) : (
                <div className="space-y-3">
                  {vulnsList.map((vuln, idx) => (
                    <div key={idx} className="bg-slate-950/80 border border-slate-800 p-3.5 rounded-xl space-y-1 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-200">{vuln.title}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                          vuln.severity === "CRITICAL" || vuln.severity === "HIGH"
                            ? "bg-rose-950 text-rose-400 border border-rose-800"
                            : "bg-amber-950 text-amber-400 border border-amber-800"
                        }`}>
                          {vuln.severity}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 leading-relaxed">{vuln.description}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right Col: Detailed Test Cases Audit List */}
          <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-cyan-400" />
              <span>Automated Authentication Security Test Suite</span>
            </h3>

            <div className="space-y-3 font-mono text-xs">
              {testsList.map((test, idx) => (
                <div key={idx} className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex items-start justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-slate-200">{test.name}</span>
                      <span className="text-[10px] text-slate-500 bg-slate-900 px-2 py-0.5 rounded">
                        {test.category}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 font-sans">{test.details}</p>
                  </div>

                  <span className={`shrink-0 px-2.5 py-1 rounded-full text-[10px] font-bold ${
                    test.passed
                      ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                      : "bg-amber-950 text-amber-400 border border-amber-800"
                  }`}>
                    {test.passed ? "PASS" : "WARN / FAIL"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
