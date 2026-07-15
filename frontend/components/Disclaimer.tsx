"use client";

import { AlertTriangle } from "lucide-react";

export default function Disclaimer({ compact = false }: { compact?: boolean }) {
  return (
    <div className={`flex gap-2 items-start ${compact ? "text-xs" : "text-sm"} bg-amber-50 border border-amber-200 rounded-xl p-3 text-amber-900`}>
      <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
      <p>
        This is AI-generated legal information, <strong>not legal advice</strong>.
        Always verify with a qualified lawyer before taking legal action.
      </p>
    </div>
  );
}
