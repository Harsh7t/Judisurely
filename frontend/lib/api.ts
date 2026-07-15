import type { AnalysisResult } from "./types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function analyzeNotice(
  text: string,
  language: string,
  templateKey: string,
  file?: File | null
): Promise<AnalysisResult> {
  const form = new FormData();
  form.append("text", text);
  form.append("language", language);
  form.append("template_key", templateKey);
  if (file) form.append("file", file);

  const res = await fetch(`${API}/api/analyze`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`Analysis failed: ${res.status}`);
  return res.json();
}

export async function downloadPdf(draftText: string): Promise<Blob> {
  const form = new FormData();
  form.append("draft_text", draftText);
  const res = await fetch(`${API}/api/pdf`, { method: "POST", body: form });
  if (!res.ok) throw new Error("PDF generation failed");
  return res.blob();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API}/api/health`);
    return res.ok;
  } catch {
    return false;
  }
}
