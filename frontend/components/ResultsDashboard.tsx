"use client";

import { useState } from "react";
import { Brain, Download, FileText, Shield, ListChecks, BookOpen, ChevronDown } from "lucide-react";
import type { AnalysisResult } from "@/lib/types";
import Disclaimer from "./Disclaimer";
import DeadlineCountdown from "./DeadlineCountdown";
import { downloadPdf } from "@/lib/api";

const TABS = [
  { id: "summary", label: "Summary", icon: FileText },
  { id: "actions", label: "Action Plan", icon: ListChecks },
  { id: "draft", label: "Legal Draft", icon: Shield },
  { id: "sources", label: "Legal Sources", icon: BookOpen },
] as const;

type TabId = (typeof TABS)[number]["id"];

export default function ResultsDashboard({ result }: { result: AnalysisResult }) {
  const [tab, setTab] = useState<TabId>("summary");
  const [draft, setDraft] = useState(result.draft_text || "");
  const [thinkingOpen, setThinkingOpen] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);

  if (result.error) {
    return <div className="card p-6 text-red-700">{result.error}</div>;
  }

  const urgency = result.reasoning?.urgency_level || "MEDIUM";
  const urgencyClass = urgency === "HIGH" ? "urgency-high" : urgency === "LOW" ? "urgency-low" : "urgency-medium";

  const handlePdf = async () => {
    setPdfLoading(true);
    try {
      const blob = await downloadPdf(draft);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "nyay_mitra_draft.pdf";
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setPdfLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="card p-5 flex flex-wrap items-center gap-4 justify-between">
        <div>
          <p className="text-sm text-muted">Document Type</p>
          <p className="font-semibold text-lg capitalize">
            {(result.extracted?.document_type as string)?.replace(/_/g, " ") || "Legal Notice"}
          </p>
        </div>
        <span className={`px-4 py-1.5 rounded-full border font-semibold text-sm ${urgencyClass}`}>
          {urgency} URGENCY
        </span>
        <DeadlineCountdown deadline={result.extracted?.deadline_date as string} />
      </div>

      <div className="card overflow-hidden">
        <div className="flex border-b border-slate-100 overflow-x-auto">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button key={id} onClick={() => setTab(id)}
              className={`flex items-center gap-2 px-5 py-3 text-sm whitespace-nowrap transition ${tab === id ? "tab-active bg-orange-50/50" : "text-muted hover:text-legal-900"}`}>
              <Icon className="w-4 h-4" /> {label}
            </button>
          ))}
        </div>

        <div className="p-6">
          {tab === "summary" && (
            <div className="space-y-4 prose-legal">
              <p className="text-lg leading-relaxed">{result.reasoning?.plain_language_summary}</p>
              <div className="grid sm:grid-cols-2 gap-3 text-sm">
                <div className="bg-slate-50 rounded-lg p-3"><span className="text-muted">From:</span> {String(result.extracted?.sender_name)}</div>
                <div className="bg-slate-50 rounded-lg p-3"><span className="text-muted">Deadline:</span> {String(result.extracted?.deadline_date || "N/A")}</div>
              </div>
              <button onClick={() => setThinkingOpen(!thinkingOpen)}
                className="flex items-center gap-2 text-saffron-dark font-medium text-sm">
                <Brain className="w-4 h-4" /> Thinking Mode — AI Reasoning
                <ChevronDown className={`w-4 h-4 transition ${thinkingOpen ? "rotate-180" : ""}`} />
              </button>
              {thinkingOpen && (
                <div className="bg-slate-50 rounded-xl p-4 text-sm text-slate-700 whitespace-pre-wrap border-l-4 border-saffron">
                  {result.thinking_md || result.reasoning?.thinking_trace}
                </div>
              )}
            </div>
          )}

          {tab === "actions" && (
            <div className="space-y-6 prose-legal">
              <section>
                <h3 className="flex items-center gap-2"><Shield className="w-5 h-5 text-saffron" /> Your Rights</h3>
                <ul>
                  {result.reasoning?.your_rights?.map((r, i) => (
                    <li key={i}><strong>{r.right}</strong> <em className="text-muted text-sm">— {r.source}</em></li>
                  ))}
                </ul>
              </section>
              <section>
                <h3>Your Options</h3>
                {result.reasoning?.your_options?.map((o, i) => (
                  <div key={i} className="bg-slate-50 rounded-lg p-3 mb-2 text-sm">
                    <strong>{o.option}</strong>
                    <p className="text-muted mt-1">Pros: {o.pros} | Cons: {o.cons}</p>
                  </div>
                ))}
              </section>
              <section>
                <h3>Action Steps</h3>
                {result.reasoning?.action_steps?.map((s) => (
                  <div key={s.step} className="border-l-4 border-saffron pl-4 mb-4">
                    <p className="font-semibold">Step {s.step}: {s.action}</p>
                    <p className="text-sm text-muted">Where: {s.where} | By: {s.deadline}</p>
                    <p className="text-sm text-muted">Documents: {s.documents_needed}</p>
                  </div>
                ))}
              </section>
            </div>
          )}

          {tab === "draft" && (
            <div className="space-y-4">
              <textarea value={draft} onChange={(e) => setDraft(e.target.value)} rows={16}
                className="w-full rounded-xl border border-slate-200 p-4 text-sm font-mono leading-relaxed focus:ring-2 focus:ring-saffron/30 outline-none" />
              <button onClick={handlePdf} disabled={pdfLoading} className="btn-primary flex items-center gap-2">
                <Download className="w-4 h-4" /> {pdfLoading ? "Generating..." : "Download PDF"}
              </button>
            </div>
          )}

          {tab === "sources" && (
            <div className="space-y-3">
              <p className="text-sm text-muted mb-4">Grounded via RAG from verified legal knowledge base (India Code)</p>
              {result.clauses?.map((c, i) => (
                <div key={i} className="bg-green-50 border border-green-200 rounded-xl p-4">
                  <p className="font-semibold text-green-900">{c.act_name}, {c.section}</p>
                  <p className="text-sm text-green-800 mt-1">{c.plain_summary}</p>
                  <p className="text-xs text-green-700 mt-2">Authority: {c.authority_to_approach}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      <Disclaimer compact />
    </div>
  );
}
