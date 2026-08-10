"use client";

import React, { useEffect, useState } from "react";
import { Workflow, Play, Terminal, CheckCircle2, AlertCircle, RefreshCw, FileText, UserCheck } from "lucide-react";
import { api } from "@/lib/api";
import { Workflow as WorkflowType, WorkflowRun, LogEntry } from "@/types";

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<WorkflowType[]>([]);
  const [runs, setRuns] = useState<WorkflowRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [executingId, setExecutingId] = useState<string | null>(null);

  // Custom execution form inputs
  const [customUser, setCustomUser] = useState("BSC/BCH/24/140");
  const [customPass, setCustomPass] = useState("Omotola");
  const [activeRun, setActiveRun] = useState<WorkflowRun | null>(null);

  const loadWorkflowData = async () => {
    setLoading(true);
    try {
      const [wData, rData] = await Promise.all([
        api.getWorkflows(),
        api.getRuns()
      ]);
      setWorkflows(wData);
      setRuns(rData);
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
    loadWorkflowData();
  }, []);

  const handleExecuteWorkflow = async (workflowId: string) => {
    setExecutingId(workflowId);
    try {
      const run = await api.runWorkflow(workflowId, {
        custom_username: customUser,
        custom_password: customPass,
      });
      setActiveRun(run);
      await loadWorkflowData();
    } catch (err: any) {
      console.error("Execution error:", err);
    } finally {
      setExecutingId(null);
    }
  };

  const parsedLogs: LogEntry[] = activeRun
    ? JSON.parse(activeRun.execution_logs || "[]")
    : [];

  const parsedExtractedData: Record<string, any> = activeRun
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
          Trigger Playwright browser automation workflows, monitor real-time execution logs, and inspect extracted data.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Col: Workflows List & Execution Controls */}
        <div className="space-y-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <UserCheck className="w-4 h-4 text-cyan-400" />
              <span>Target Portal Credentials</span>
            </h2>

            <div className="space-y-3 text-xs font-mono">
              <div className="space-y-1">
                <label className="text-slate-400 block font-sans">User ID / Matric No</label>
                <input
                  type="text"
                  value={customUser}
                  onChange={(e) => setCustomUser(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-cyan-300 font-bold focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-400 block font-sans">Password</label>
                <input
                  type="password"
                  value={customPass}
                  onChange={(e) => setCustomPass(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200 focus:outline-none focus:border-cyan-500"
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
          {/* Active Run Header */}
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

            {/* Extracted Data Card */}
            {parsedExtractedData && Object.keys(parsedExtractedData).length > 0 && (
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
                <h3 className="text-xs font-bold text-emerald-400 font-mono uppercase tracking-wider">
                  Extracted Student Profile Records
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
                  <div>Name: <span className="text-white font-bold">{parsedExtractedData.full_name}</span></div>
                  <div>Matric No: <span className="text-cyan-400 font-bold">{parsedExtractedData.student_id || parsedExtractedData.matric_no}</span></div>
                  <div>Faculty: <span className="text-slate-300">{parsedExtractedData.faculty}</span></div>
                  <div>Department: <span className="text-slate-300">{parsedExtractedData.department}</span></div>
                  <div>Programme: <span className="text-slate-300">{parsedExtractedData.programme}</span></div>
                  <div>Level: <span className="text-slate-300">{parsedExtractedData.current_level}</span></div>
                </div>
              </div>
            )}

            {/* Console Log Window */}
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 font-mono text-xs space-y-2 max-h-96 overflow-y-auto">
              <div className="text-slate-500 pb-2 border-b border-slate-900 flex items-center justify-between">
                <span>// PLAYWRIGHT AUTOMATION ENGINE CONSOLE LOGS</span>
                <span>{parsedLogs.length} events</span>
              </div>

              {parsedLogs.length === 0 ? (
                <div className="text-slate-600 py-6 text-center">
                  No log output. Click "Execute Run" to start workflow.
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
