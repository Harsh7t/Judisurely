"use client";

import { useEffect, useState } from "react";
import { Clock } from "lucide-react";

export default function DeadlineCountdown({ deadline }: { deadline?: string | null }) {
  const [daysLeft, setDaysLeft] = useState<number | null>(null);

  useEffect(() => {
    if (!deadline || deadline === "Unknown" || deadline === "null") return;
    const parts = deadline.split("/");
    if (parts.length !== 3) return;
    const [d, m, y] = parts.map(Number);
    const dl = new Date(y, m - 1, d);
    const diff = Math.ceil((dl.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
    setDaysLeft(diff);
  }, [deadline]);

  if (daysLeft === null) return null;

  const urgent = daysLeft <= 7;
  return (
    <div className={`flex items-center gap-2 px-4 py-2 rounded-xl border ${urgent ? "bg-red-50 border-red-200 text-red-800" : "bg-blue-50 border-blue-200 text-blue-800"}`}>
      <Clock className="w-5 h-5" />
      <span className="font-semibold">
        {daysLeft >= 0 ? `${daysLeft} days left to respond` : `${Math.abs(daysLeft)} days overdue`}
      </span>
    </div>
  );
}
