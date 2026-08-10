"use client";

import React, { useEffect, useState } from "react";
import { FileText, Download, Plus, RefreshCw, FileCode, CheckCircle2 } from "lucide-react";
import { api } from "@/lib/api";
import { Document as DocumentType } from "@/types";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentType[]>([]);
  const [loading, setLoading] = useState(true);

  // PDF Renderer state
  const [showRenderModal, setShowRenderModal] = useState(false);
  const [renderTitle, setRenderTitle] = useState("FUW Student Verification Report — BSC/BCH/24/140");
  const [renderFormat, setRenderFormat] = useState("A4");
  const [renderHtml, setRenderHtml] = useState(`<!DOCTYPE html>
<html>
<head>
  <style>
    @page { size: A4; margin: 15mm; }
    body { font-family: Arial, sans-serif; color: #0f172a; padding: 10px; }
    h1 { color: #0284c7; font-size: 22px; border-bottom: 2px solid #0284c7; padding-bottom: 6px; }
    .card { border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; margin-top: 15px; }
    .label { font-weight: bold; color: #64748b; }
  </style>
</head>
<body>
  <h1>Federal University Wukari — Student Verification Report</h1>
  <div class="card">
    <p><span class="label">Student Name:</span> IBRAHIM, Abibat Abiodun</p>
    <p><span class="label">Matriculation No:</span> BSC/BCH/24/140</p>
    <p><span class="label">Department:</span> Biochemistry</p>
    <p><span class="label">Level:</span> 200</p>
    <p><span class="label">Verification Status:</span> PASS — Live Portal Validated</p>
  </div>
</body>
</html>`);

  const [rendering, setRendering] = useState(false);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const data = await api.getDocuments();
      setDocuments(data);
    } catch (err) {
      console.error("Documents load error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleRenderPdf = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!renderTitle || !renderHtml) return;
    setRendering(true);
    try {
      await api.renderPdf(renderTitle, renderHtml, renderFormat);
      setShowRenderModal(false);
      await loadDocuments();
    } catch (err) {
      console.error("Render PDF error:", err);
    } finally {
      setRendering(false);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <FileText className="w-6 h-6 text-emerald-400" />
            <span>Document Studio & A4/A5 PDF Renderer</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Standardized document generation engine with custom margins, print CSS rules, and downloadable PDF assets.
          </p>
        </div>

        <button
          onClick={() => setShowRenderModal(true)}
          className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-all flex items-center gap-2 shadow-lg shadow-emerald-600/20"
        >
          <Plus className="w-4 h-4" />
          <span>Render Custom PDF</span>
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-500 text-xs font-mono animate-pulse">
          Loading generated PDF documents...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {documents.map((doc) => (
            <div key={doc.id} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4 flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px] font-mono font-bold">
                    {doc.page_format} FORMAT
                  </span>
                  <span className="text-[11px] font-mono text-slate-500">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white leading-snug">{doc.title}</h3>
                <p className="text-xs text-slate-400 font-mono">
                  Pages: {doc.page_count} • Standardized Playwright PDF
                </p>
              </div>

              <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                <span className="text-[11px] font-mono text-slate-500">
                  {Math.round((doc.file_size_bytes || 1024) / 1024)} KB
                </span>

                <a
                  href={api.getDownloadUrl(doc.id)}
                  target="_blank"
                  rel="noreferrer"
                  className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition-all flex items-center gap-1.5 shadow-md shadow-emerald-600/20"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download PDF</span>
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Render PDF Modal */}
      {showRenderModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 space-y-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h3 className="text-base font-bold text-white">Render Custom Standardized PDF</h3>
              <button onClick={() => setShowRenderModal(false)} className="text-slate-400 hover:text-slate-200 text-xs">Close</button>
            </div>

            <form onSubmit={handleRenderPdf} className="space-y-4 text-xs font-mono">
              <div className="grid grid-cols-3 gap-4">
                <div className="col-span-2 space-y-1.5">
                  <label className="text-slate-300 block font-sans">Document Title</label>
                  <input
                    type="text"
                    required
                    value={renderTitle}
                    onChange={(e) => setRenderTitle(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-100 focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-slate-300 block font-sans">Paper Size</label>
                  <select
                    value={renderFormat}
                    onChange={(e) => setRenderFormat(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-100 focus:outline-none focus:border-emerald-500"
                  >
                    <option value="A4">A4 Standard</option>
                    <option value="A5">A5 Compact</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-slate-300 block font-sans">HTML Template Content</label>
                <textarea
                  rows={8}
                  required
                  value={renderHtml}
                  onChange={(e) => setRenderHtml(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 font-mono text-[11px] focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowRenderModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-sans text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={rendering}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-sans text-xs font-semibold flex items-center gap-2"
                >
                  {rendering ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Generating PDF...</span>
                    </>
                  ) : (
                    <span>Compile PDF</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
