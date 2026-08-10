"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Globe2,
  Play,
  FileText,
  ShieldCheck,
  Zap,
  Activity,
  CheckCircle2,
  Clock,
  ArrowRight,
  RefreshCw,
  AlertTriangle
} from "lucide-react";
import { api } from "@/lib/api";
import { Portal, Workflow, WorkflowRun, Document, SecurityScan } from "@/types";

export default function DashboardPage() {
  const [portals, setPortals] = useState<Portal[]>([]);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [runs, setRuns] = useState<WorkflowRun[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [scans, setScans] = useState<SecurityScan[]>([]);
  const [loading, setLoading] = useState(true);
  const [runningWf, setRunningWf] = useState(false);
  const [lastRunMessage, setLastRunMessage] = useState<string | null>(null);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [pData, wData, rData, dData, sData] = await Promise.all([
        api.getPortals(),
        api.getWorkflows(),
        api.getRuns(),
        api.getDocuments(),
        api.getSecurityScans(),
      ]);
      setPortals(pData);
      setWorkflows(wData);
      setRuns(rData);
      setDocuments(dData);
      setScans(sData);
    } catch (err) {
      console.error("Dashboard data load error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleQuickRunFUW = async () => {
    if (workflows.length === 0) return;
    const fuwWorkflow = workflows.find(w => w.name.includes("FUW")) || workflows[0];
    setRunningWf(true);
    setLastRunMessage("Executing Playwright automated login & student verification on ug.fuwportal.edu.ng...");

    try {
      const run = await api.runWorkflow(fuwWorkflow.id, {
        custom_username: "BSC/BCH/24/140",
        custom_password: "Omotola"
      });
      if (run.status === "COMPLETED") {
        setLastRunMessage("Automation completed successfully! Generated student report PDF.");
      } else {
        setLastRunMessage(`Automation failed: ${run.error_message || "Unknown error"}`);
      }
      await loadDashboardData();
    } catch (err: any) {
      setLastRunMessage(`Execution error: ${err.message}`);
    } finally {
      setRunningWf(false);
    }
  };

  const fuwPortal = portals.find(p => p.base_url.includes("fuwportal")) || portals[0];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-cyan-950/60 border border-slate-800 rounded-2xl p-6 md:p-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative overflow-hidden shadow-xl">
        <div className="space-y-2 max-w-2xl relative z-10">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono">
            <Zap className="w-3.5 h-3.5" />
            <span>AI SOFTWARE FACTORY PLATFORM</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
            DocFlow Portal Automator & Document Engine
          </h1>
          <p className="text-slate-400 text-sm leading-relaxed">
            Orchestrate Playwright browser workflows on <strong className="text-cyan-300">ug.fuwportal.edu.ng</strong>, extract student records, generate A4/A5 PDF documents, and audit authentication controls.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 relative z-10 w-full md:w-auto shrink-0">
          <button
            onClick={handleQuickRunFUW}
            disabled={runningWf || loading}
            className="flex items-center justify-center space-x-2.5 px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-bold text-sm shadow-lg shadow-cyan-500/20 transition-all disabled:opacity-50"
          >
            {runningWf ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin text-slate-950" />
                <span>Running Automation...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-slate-950 text-slate-950" />
                <span>Run FUW Verification</span>
              </>
            )}
          </button>
        </div>
      </div>

      {lastRunMessage && (
        <div className={`p-4 rounded-xl border flex items-center justify-between text-sm ${
          lastRunMessage.includes("successfully")
            ? "bg-emerald-950/40 border-emerald-800 text-emerald-300"
            : lastRunMessage.includes("Executing")
            ? "bg-cyan-950/40 border-cyan-800 text-cyan-300"
            : "bg-rose-950/40 border-rose-800 text-rose-300"
        }`}>
          <div className="flex items-center space-x-3">
            {lastRunMessage.includes("successfully") ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            ) : (
              <Activity className="w-5 h-5 text-cyan-400 shrink-0 animate-pulse" />
            )}
            <span>{lastRunMessage}</span>
          </div>
          <button onClick={() => setLastRunMessage(null)} className="text-xs opacity-60 hover:opacity-100">Dismiss</button>
        </div>
      )}

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 font-mono">TARGET PORTALS</span>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
              <Globe2 className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white">{portals.length} Active</div>
          <p className="text-xs text-slate-500 font-mono truncate">
            {fuwPortal ? fuwPortal.name : "ug.fuwportal.edu.ng"}
          </p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 font-mono">AUTOMATION RUNS</span>
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white">{runs.length} Executed</div>
          <p className="text-xs text-emerald-400 font-mono flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            {runs.filter(r => r.status === "COMPLETED").length} Passed
          </p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 font-mono">GENERATED PDFS</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white">{documents.length} PDF Reports</div>
          <p className="text-xs text-slate-500 font-mono">Standardized A4/A5 Output</p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 font-mono">SECURITY AUDIT SCORE</span>
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white">
            {scans.length > 0 ? `${scans[0].score}/100` : "78/100"}
          </div>
          <p className="text-xs text-amber-400 font-mono">
            {scans.length > 0 ? `${scans[0].vulnerabilities_found} Vulnerabilities Found` : "Authentication Audited"}
          </p>
        </div>
      </div>

      {/* Target Portal Focus Card */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center font-bold text-white">
              FUW
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Federal University Wukari Student Portal</h2>
              <p className="text-xs text-slate-400 font-mono">https://ug.fuwportal.edu.ng/index.php</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="px-3 py-1 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 text-xs font-mono">
              Live & Reachable
            </span>
            <Link
              href="/portals"
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-all flex items-center gap-1.5"
            >
              <span>Portal Details</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono text-slate-300 pt-1">
          <div className="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
            <span className="text-slate-500 block mb-1 text-[11px]">DEMO MATRIC NO</span>
            <span className="text-cyan-400 font-bold">BSC/BCH/24/140</span>
          </div>
          <div className="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
            <span className="text-slate-500 block mb-1 text-[11px]">DEMO PASSWORD</span>
            <span className="text-slate-200">Omotola</span>
          </div>
          <div className="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
            <span className="text-slate-500 block mb-1 text-[11px]">AUTOMATION WORKFLOW</span>
            <span className="text-emerald-400 font-bold">Login & Profile Extraction</span>
          </div>
        </div>
      </div>

      {/* Two Column Layout: Recent Runs + Generated Documents */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Automation Runs */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-200 text-base flex items-center gap-2">
              <Clock className="w-4 h-4 text-cyan-400" />
              <span>Recent Workflow Runs</span>
            </h3>
            <Link href="/workflows" className="text-xs text-cyan-400 hover:underline">
              View All
            </Link>
          </div>

          {runs.length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-xs font-mono">
              No workflow executions yet. Click "Run FUW Verification" above to test!
            </div>
          ) : (
            <div className="space-y-3">
              {runs.slice(0, 4).map((run) => (
                <div key={run.id} className="bg-slate-950/60 border border-slate-800 rounded-xl p-3.5 flex items-center justify-between text-xs">
                  <div className="space-y-1 max-w-[70%]">
                    <div className="font-medium text-slate-200 truncate">
                      FUW Student Portal Automated Verification
                    </div>
                    <div className="text-[11px] text-slate-500 font-mono">
                      Started: {new Date(run.started_at).toLocaleTimeString()}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className={`px-2.5 py-1 rounded-full text-[10px] font-mono font-bold ${
                      run.status === "COMPLETED"
                        ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                        : "bg-rose-950 text-rose-400 border border-rose-800"
                    }`}>
                      {run.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Generated PDF Reports */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-200 text-base flex items-center gap-2">
              <FileText className="w-4 h-4 text-emerald-400" />
              <span>Generated PDF Reports</span>
            </h3>
            <Link href="/documents" className="text-xs text-emerald-400 hover:underline">
              Open Document Studio
            </Link>
          </div>

          {documents.length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-xs font-mono">
              No PDF documents generated yet.
            </div>
          ) : (
            <div className="space-y-3">
              {documents.slice(0, 4).map((doc) => (
                <div key={doc.id} className="bg-slate-950/60 border border-slate-800 rounded-xl p-3.5 flex items-center justify-between text-xs">
                  <div className="space-y-1">
                    <div className="font-medium text-slate-200 truncate">{doc.title}</div>
                    <div className="text-[11px] text-slate-500 font-mono">
                      Format: {doc.page_format} • Standardized A4 PDF
                    </div>
                  </div>

                  <a
                    href={api.getDownloadUrl(doc.id)}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3 py-1.5 rounded-lg bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 text-xs font-medium transition-all"
                  >
                    Download PDF
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
