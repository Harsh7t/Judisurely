"use client";

import { History, Trash2 } from "lucide-react";
import type { CaseRecord } from "@/lib/types";

interface Props {
  cases: CaseRecord[];
  onSelect: (c: CaseRecord) => void;
  onClear: () => void;
}

export default function CaseHistory({ cases, onSelect, onClear }: Props) {
  if (cases.length === 0) return null;

  return (
    <div className="card p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold flex items-center gap-2 text-legal-900">
          <History className="w-4 h-4" /> Recent Cases
        </h3>
        <button onClick={onClear} className="text-xs text-red-600 hover:underline flex items-center gap-1">
          <Trash2 className="w-3 h-3" /> Clear
        </button>
      </div>
      <div className="space-y-2 max-h-48 overflow-y-auto">
        {cases.map((c) => (
          <button key={c.id} onClick={() => onSelect(c)}
            className="w-full text-left p-2 rounded-lg hover:bg-orange-50 text-sm transition">
            <p className="font-medium truncate">{c.title}</p>
            <p className="text-xs text-muted">{c.date} · {c.urgency}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
