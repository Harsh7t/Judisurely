"use client";

import { useEffect, useState } from "react";
import { Scale, Wifi, WifiOff } from "lucide-react";
import { checkHealth } from "@/lib/api";

export default function Header() {
  const [online, setOnline] = useState<boolean | null>(null);

  useEffect(() => {
    checkHealth().then(setOnline);
  }, []);

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur border-b border-orange-100">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-saffron to-saffron-dark flex items-center justify-center">
            <Scale className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-display text-xl font-bold text-legal-900">Judisurely</h1>
            <p className="text-xs text-muted">AI Legal Action Engine</p>
          </div>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span className="hidden sm:inline text-muted">Powered by Gemma 4</span>
          {online === null ? null : online ? (
            <span className="flex items-center gap-1 text-green-700"><Wifi className="w-4 h-4" /> API Ready</span>
          ) : (
            <span className="flex items-center gap-1 text-red-600"><WifiOff className="w-4 h-4" /> API Offline</span>
          )}
        </div>
      </div>
    </header>
  );
}
