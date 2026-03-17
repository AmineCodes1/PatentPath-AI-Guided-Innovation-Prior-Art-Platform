/**
 * Search session history tab for a project workspace.
 */

import type { ReactElement } from "react";
import type { ProjectSessionSummary, ProjectTimelineEvent } from "../../types/project";

type SearchHistoryTabProps = {
  sessions: ProjectSessionSummary[];
  timeline: ProjectTimelineEvent[];
  onRerunSearch: (sessionId: string) => void;
  onViewResults: (sessionId: string) => void;
};

const STATUS_STYLES: Record<ProjectSessionSummary["status"], string> = {
  PENDING: "bg-slate-200 text-slate-700",
  PROCESSING: "bg-accent/20 text-primary",
  COMPLETE: "bg-risk-low/15 text-risk-low",
  FAILED: "bg-risk-high/15 text-risk-high",
};

function findSessionRisk(sessionId: string, timeline: ProjectTimelineEvent[]): "HIGH" | "MEDIUM" | "LOW" | null {
  const analysisEvent = timeline.find(
    (event) => event.event_type === "ANALYSIS" && event.session_id === sessionId,
  );

  if (!analysisEvent) {
    return null;
  }

  if (analysisEvent.summary.includes("HIGH")) {
    return "HIGH";
  }
  if (analysisEvent.summary.includes("MEDIUM")) {
    return "MEDIUM";
  }
  if (analysisEvent.summary.includes("LOW")) {
    return "LOW";
  }
  return null;
}

function riskStyle(risk: "HIGH" | "MEDIUM" | "LOW" | null): string {
  if (risk === "HIGH") {
    return "bg-risk-high/15 text-risk-high";
  }
  if (risk === "MEDIUM") {
    return "bg-risk-medium/15 text-risk-medium";
  }
  if (risk === "LOW") {
    return "bg-risk-low/15 text-risk-low";
  }
  return "bg-slate-200 text-slate-700";
}

export default function SearchHistoryTab({
  sessions,
  timeline,
  onRerunSearch,
  onViewResults,
}: Readonly<SearchHistoryTabProps>): ReactElement {
  if (sessions.length === 0) {
    return (
      <div className="rounded-xl bg-surface p-4 text-sm text-text-secondary">
        No search sessions yet for this project.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {sessions.map((session) => {
        const risk = findSessionRisk(session.id, timeline);
        return (
          <article key={session.id} className="rounded-xl border border-slate-200 bg-white p-4">
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <p className="text-sm font-semibold text-text-primary">
                  {new Date(session.executed_at).toLocaleString()}
                </p>
                <p className="mt-1 line-clamp-2 text-sm text-text-secondary">{session.query_text}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${STATUS_STYLES[session.status]}`}>
                  {session.status}
                </span>
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${riskStyle(risk)}`}>
                  Risk: {risk ?? "N/A"}
                </span>
              </div>
            </div>

            <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
              <p className="text-xs text-text-secondary">{session.result_count} results</p>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => onRerunSearch(session.id)}
                  className="rounded-lg border border-primary px-3 py-1.5 text-xs font-semibold text-primary transition hover:bg-primary hover:text-white"
                >
                  Re-run Search
                </button>
                <button
                  type="button"
                  onClick={() => onViewResults(session.id)}
                  className="rounded-lg bg-primary px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-blue-900"
                >
                  View Results
                </button>
              </div>
            </div>
          </article>
        );
      })}
    </div>
  );
}
