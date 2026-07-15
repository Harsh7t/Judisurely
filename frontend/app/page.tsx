"use client";

import { useCallback, useEffect, useState } from "react";
import { ArrowRight, Scale, Zap, Shield, Globe, Users } from "lucide-react";
import UploadPanel from "@/components/UploadPanel";
import ResultsDashboard from "@/components/ResultsDashboard";
import CaseHistory from "@/components/CaseHistory";
import Disclaimer from "@/components/Disclaimer";
import type { AnalysisResult, CaseRecord } from "@/lib/types";

const FEATURES = [
  { icon: Zap, title: "60-Second Analysis", desc: "Upload → understand → act in under a minute" },
  { icon: Shield, title: "RAG-Grounded", desc: "Every claim backed by verified Indian law clauses" },
  { icon: Globe, title: "Hindi + English", desc: "Multilingual output powered by Gemma 4" },
  { icon: Users, title: "Built for Citizens", desc: "3 crore pending cases — first step should be free" },
];

export default function Home() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<CaseRecord[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem("nyay_cases");
    if (saved) setHistory(JSON.parse(saved));
  }, []);

  const saveCase = useCallback((r: AnalysisResult) => {
    const record: CaseRecord = {
      id: Date.now().toString(),
      title: String(r.extracted?.summary_one_line || "Legal Notice").slice(0, 60),
      date: new Date().toLocaleDateString("en-IN"),
      urgency: r.reasoning?.urgency_level || "MEDIUM",
      result: r,
    };
    const updated = [record, ...history].slice(0, 10);
    setHistory(updated);
    localStorage.setItem("nyay_cases", JSON.stringify(updated));
  }, [history]);

  const handleResult = useCallback((r: AnalysisResult) => {
    setResult(r);
    if (!r.error) saveCase(r);
  }, [saveCase]);

  return (
    <main>
      {/* Hero */}
      <section className="gradient-hero py-16 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-white/80 rounded-full px-4 py-1.5 text-sm text-saffron-dark font-medium mb-6 border border-orange-200">
            <Scale className="w-4 h-4" /> Track 1: AI for Legal Assistance · Gemma 4
          </div>
          <h1 className="font-display text-4xl sm:text-5xl font-bold text-legal-900 mb-4 leading-tight">
            From Confusion to <span className="text-saffron">Action</span>
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto mb-8">
            Upload your legal notice. Get plain-language explanation, your rights,
            step-by-step action plan, and a ready-to-use legal draft — in seconds.
          </p>
          <div className="flex flex-wrap justify-center gap-6 text-sm text-muted">
            <span>30M+ pending cases in India</span>
            <span>·</span>
            <span>₹1,500–5,000 avg. lawyer consultation</span>
            <span>·</span>
            <span className="text-saffron-dark font-semibold">First step: ₹0</span>
          </div>
        </div>
      </section>

      {/* Features strip */}
      <section className="max-w-6xl mx-auto px-4 -mt-6">
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {FEATURES.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="card p-4 text-center">
              <Icon className="w-8 h-8 text-saffron mx-auto mb-2" />
              <h3 className="font-semibold text-sm">{title}</h3>
              <p className="text-xs text-muted mt-1">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Main app */}
      <section className="max-w-6xl mx-auto px-4 py-12">
        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1 space-y-4">
            <UploadPanel onResult={handleResult} loading={loading} setLoading={setLoading} />
            <CaseHistory cases={history} onSelect={(c) => setResult(c.result)}
              onClear={() => { setHistory([]); localStorage.removeItem("nyay_cases"); }} />
            <Disclaimer />
          </div>
          <div className="lg:col-span-2">
            {result ? (
              <ResultsDashboard result={result} />
            ) : (
              <div className="card p-12 text-center text-muted">
                <ArrowRight className="w-12 h-12 mx-auto mb-4 text-saffron/40" />
                <p className="text-lg">Upload or paste a legal notice to get started</p>
                <p className="text-sm mt-2">Try a sample from <code className="bg-slate-100 px-1 rounded">data/sample_notices/</code></p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="bg-legal-900 text-white py-16 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="font-display text-2xl font-bold mb-8">How Nyay Mitra Works</h2>
          <div className="grid sm:grid-cols-4 gap-6 text-sm">
            {["Gemma extracts notice", "RAG finds real laws", "Gemma reasons & plans", "Download your draft"].map((step, i) => (
              <div key={step}>
                <div className="w-10 h-10 rounded-full bg-saffron text-white font-bold flex items-center justify-center mx-auto mb-2">{i + 1}</div>
                <p>{step}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="text-center py-8 text-sm text-muted">
        Nyay Mitra · Harshit, Prem, Shreya · Build with Gemma – AIMS DTU
      </footer>
    </main>
  );
}
