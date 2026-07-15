"use client";

import { useCallback, useState } from "react";
import { FileText, Loader2, Upload } from "lucide-react";
import type { AnalysisResult } from "@/lib/types";
import { analyzeNotice } from "@/lib/api";

const TEMPLATES = [
  { key: "legal_reply", label: "Legal Reply" },
  { key: "consumer_complaint", label: "Consumer Complaint" },
  { key: "rti_application", label: "RTI Application" },
];

interface Props {
  onResult: (result: AnalysisResult) => void;
  loading: boolean;
  setLoading: (v: boolean) => void;
}

export default function UploadPanel({ onResult, loading, setLoading }: Props) {
  const [text, setText] = useState("");
  const [language, setLanguage] = useState("English");
  const [template, setTemplate] = useState("legal_reply");
  const [file, setFile] = useState<File | null>(null);
  const [drag, setDrag] = useState(false);

  const handleAnalyze = useCallback(async () => {
    if (!text.trim() && !file) return;
    setLoading(true);
    try {
      const result = await analyzeNotice(text, language, template, file);
      onResult(result);
    } catch (e) {
      onResult({ error: String(e) });
    } finally {
      setLoading(false);
    }
  }, [text, language, template, file, onResult, setLoading]);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDrag(false);
    const f = e.dataTransfer.files[0];
    if (f) setFile(f);
  };

  return (
    <div className="card p-6 space-y-5">
      <h2 className="text-xl font-semibold text-legal-900">Upload Your Legal Notice</h2>

      <div
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={onDrop}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition ${drag ? "border-saffron bg-orange-50" : "border-slate-200 hover:border-saffron/50"}`}
      >
        <Upload className="w-10 h-10 mx-auto text-saffron mb-2" />
        <p className="text-slate-600 mb-3">Drag & drop PDF, image, or text file</p>
        <label className="btn-secondary inline-block cursor-pointer">
          Choose File
          <input type="file" className="hidden" accept=".pdf,.txt,.png,.jpg,.jpeg"
            onChange={(e) => setFile(e.target.files?.[0] || null)} />
        </label>
        {file && <p className="mt-2 text-sm text-saffron-dark font-medium">{file.name}</p>}
      </div>

      <div>
        <label className="text-sm font-medium text-slate-700 mb-1 block">Or paste notice text</label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={6}
          placeholder="Paste your legal notice here..."
          className="w-full rounded-xl border border-slate-200 p-4 text-sm focus:ring-2 focus:ring-saffron/30 focus:border-saffron outline-none resize-none"
        />
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-medium text-slate-700 mb-2 block">Output Language</label>
          <div className="flex gap-2">
            {["English", "Hindi"].map((lang) => (
              <button key={lang} onClick={() => setLanguage(lang)}
                className={`flex-1 py-2 rounded-lg border text-sm font-medium transition ${language === lang ? "bg-saffron text-white border-saffron" : "bg-white border-slate-200 hover:border-saffron"}`}>
                {lang}
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="text-sm font-medium text-slate-700 mb-2 block">Draft Template</label>
          <select value={template} onChange={(e) => setTemplate(e.target.value)}
            className="w-full rounded-lg border border-slate-200 p-2.5 text-sm focus:ring-2 focus:ring-saffron/30 outline-none">
            {TEMPLATES.map((t) => <option key={t.key} value={t.key}>{t.label}</option>)}
          </select>
        </div>
      </div>

      <button onClick={handleAnalyze} disabled={loading || (!text.trim() && !file)} className="btn-primary w-full flex items-center justify-center gap-2">
        {loading ? <><Loader2 className="w-5 h-5 animate-spin" /> Analyzing with Gemma 4...</> : <><FileText className="w-5 h-5" /> Analyze My Notice</>}
      </button>
    </div>
  );
}
