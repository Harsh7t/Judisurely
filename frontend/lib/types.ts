export interface AnalysisResult {
  summary_md?: string;
  urgency_md?: string;
  thinking_md?: string;
  action_md?: string;
  draft_text?: string;
  extracted?: Record<string, unknown>;
  reasoning?: {
    urgency_level?: string;
    plain_language_summary?: string;
    your_rights?: { right: string; source: string }[];
    your_options?: { option: string; pros: string; cons: string }[];
    action_steps?: {
      step: number;
      action: string;
      where: string;
      deadline: string;
      documents_needed: string;
    }[];
    thinking_trace?: string;
  };
  clauses?: {
    act_name: string;
    section: string;
    plain_summary: string;
    authority_to_approach?: string;
  }[];
  error?: string;
}

export interface CaseRecord {
  id: string;
  title: string;
  date: string;
  urgency: string;
  result: AnalysisResult;
}
