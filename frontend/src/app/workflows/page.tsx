"use client";

import React, { useEffect, useState } from "react";
import { Workflow, Play, Terminal, RefreshCw, KeyRound } from "lucide-react";
import { api } from "@/lib/api";
import { Workflow as WorkflowType, WorkflowRun, LogEntry } from "@/types";

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<WorkflowType[]>([]);
  const [loading, setLoading] = useState(true);
  const [executingId, setExecutingId] = useState<string | null>(null);

  // Dynamic credentials inputs - empty by default for any portal user
  const [customUser, setCustomUser] = useState("");
  const [customPass, setCustomPass] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeRun, setActiveRun] = useState<WorkflowRun | null>(null);

  const loadWorkflowData = async () => {
    setLoading(true);
    try {
      const [wData, rData] = await Promise.all([
        api.getWorkflows(),
        api.getRuns()
      ]);
      setWorkflows(wData);
      if (rData.length > 0 && !activeRun) {
        setActiveRun(rData[0]);
      }
    } catch (err) {
      console.error("Workflow load error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadWorkflowData();
    // Initial operator console load only.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleExecuteWorkflow = async (workflowId: string) => {
    setErrorMessage(null);
    if (!customUser || !customPass) {
      setErrorMessage("Please enter student User ID (e.g. ENG/COE/21/013) and password.");
      return;
    }

    setExecutingId(workflowId);
    try {
      const run = await api.runWorkflow(workflowId, {
        custom_username: customUser,
        custom_password: customPass,
      });
      setActiveRun(run);
      await loadWorkflowData();
    } catch (err: unknown) {
      console.error("Execution error:", err);
      setErrorMessage(err instanceof Error ? err.message : "Failed to execute portal automation");
    } finally {
      setExecutingId(null);
    }
  };

  const parsedLogs: LogEntry[] = activeRun
    ? JSON.parse(activeRun.execution_logs || "[]")
    : [];

  const parsedExtractedData: Record<string, unknown> = activeRun
    ? JSON.parse(activeRun.extracted_data_json || "{}")
    : {};

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="border-b border-slate-800 pb-6">
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <Workflow className="w-6 h-6 text-cyan-400" />
          <span>Workflow Orchestrator & Live Execution Console</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Input student credentials dynamically, trigger Playwright browser automation workflows, and export exact PDF documents.
        </p>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-950/50 border border-rose-800 text-rose-300 text-xs font-mono flex items-center justify-between">
          <span>⚠️ {errorMessage}</span>
          <button onClick={() => setErrorMessage(null)} className="text-slate-400 hover:text-slate-200">Dismiss</button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Col: Dynamic Credentials & Workflows List */}
        <div className="space-y-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <KeyRound className="w-4 h-4 text-cyan-400" />
              <span>Input Student Portal Credentials</span>
            </h2>

            <div className="space-y-3 text-xs font-mono">
              <div className="space-y-1">
                <label className="text-slate-300 block font-sans font-semibold">Student User ID / Reg No</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. ENG/COE/21/013 or BSC/BCH/24/140"
                  value={customUser}
                  onChange={(e) => setCustomUser(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-cyan-300 font-bold focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-300 block font-sans font-semibold">Password</label>
                <input
                  type="password"
                  required
                  placeholder="Enter portal passcode"
                  value={customPass}
                  onChange={(e) => setCustomPass(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4">
            <h2 className="text-sm font-bold text-white">Configured Workflows</h2>

            {loading ? (
              <div className="text-center py-6 text-slate-500 text-xs font-mono animate-pulse">
                Loading workflows...
              </div>
            ) : (
              <div className="space-y-4">
                {workflows.map((wf) => (
                  <div key={wf.id} className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 space-y-3">
                    <div>
                      <h3 className="text-xs font-bold text-white leading-snug">{wf.name}</h3>
                      <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">{wf.description}</p>
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-slate-900">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        Format: {wf.target_format} PDF
                      </span>

                      <button
                        onClick={() => handleExecuteWorkflow(wf.id)}
                        disabled={executingId === wf.id}
                        className="px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold transition-all flex items-center gap-1.5 shadow-md shadow-cyan-600/20 disabled:opacity-50"
                      >
                        {executingId === wf.id ? (
                          <>
                            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                            <span>Running...</span>
                          </>
                        ) : (
                          <>
                            <Play className="w-3.5 h-3.5 fill-white" />
                            <span>Execute Run</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Col: Live Execution Log Console & Extracted Results */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="space-y-1">
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <Terminal className="w-5 h-5 text-cyan-400" />
                  <span>Execution Output Console</span>
                </h2>
                {activeRun && (
                  <p className="text-xs font-mono text-slate-400">Run ID: {activeRun.id}</p>
                )}
              </div>

              {activeRun && (
                <span className={`px-3 py-1 rounded-full text-xs font-mono font-bold ${
                  activeRun.status === "COMPLETED"
                    ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                    : "bg-rose-950 text-rose-400 border border-rose-800"
                }`}>
                  {activeRun.status}
                </span>
              )}
            </div>

            {/* Extracted Data Result Card */}
            {parsedExtractedData && Object.keys(parsedExtractedData).length > 0 && (
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
                <h3 className="text-xs font-bold text-emerald-400 font-mono uppercase tracking-wider">
                  Extracted Student Record Summary
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
                  <div>User ID: <span className="text-cyan-400 font-bold">{String(parsedExtractedData.student_id || "")}</span></div>
                  <div>Portal Webview: <span className="text-slate-300">{String(parsedExtractedData.popup_webview_url || "https://ug.fuwportal.edu.ng/exam_card_printout.php")}</span></div>
                </div>
              </div>
            )}

            {/* Console Log Window */}
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 font-mono text-xs space-y-2 max-h-96 overflow-y-auto">
              <div className="text-slate-500 pb-2 border-b border-slate-900 flex items-center justify-between">
                <span>{`// PLAYWRIGHT AUTOMATION ENGINE CONSOLE LOGS`}</span>
                <span>{parsedLogs.length} events</span>
              </div>

              {parsedLogs.length === 0 ? (
                <div className="text-slate-600 py-6 text-center">
                  No log output. Input credentials on the left and click Execute Run.
                </div>
              ) : (
                parsedLogs.map((log, idx) => (
                  <div key={idx} className="flex items-start space-x-3 text-[11px] leading-relaxed">
                    <span className="text-slate-600 shrink-0">[{log.timestamp}]</span>
                    <span className={log.level === "ERROR" ? "text-rose-400" : "text-cyan-300"}>
                      {log.message}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
