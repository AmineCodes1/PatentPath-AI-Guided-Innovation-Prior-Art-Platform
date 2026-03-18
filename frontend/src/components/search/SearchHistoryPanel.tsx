/**
 * Slide-out search history drawer grouped by project with rerun/view actions.
 */

import { useEffect, useMemo, useState } from "react";
import type { ReactElement } from "react";
import { useNavigate } from "react-router-dom";
import { getGapAnalysis } from "../../api/analysis";
import { getProjects, getProjectSessions } from "../../api/projects";
import type { InnovationProject, ProjectSessionSummary } from "../../types/project";
import type { OverallRisk } from "../../types/analysis";

type SearchHistoryPanelProps = {
  open: boolean;
  onClose: () => void;
};

type SessionHistoryItem = {
  session: ProjectSessionSummary;
  risk: OverallRisk | "UNKNOWN";
};

type ProjectHistoryGroup = {
  project: InnovationProject;
  entries: SessionHistoryItem[];
};

function compareSessionDateDesc(left: SessionHistoryItem, right: SessionHistoryItem): number {
  return new Date(right.session.executed_at).getTime() - new Date(left.session.executed_at).getTime();
}

function riskBadgeClass(risk: OverallRisk | "UNKNOWN"): string {
  if (risk === "HIGH") {
    return "bg-risk-high/15 text-risk-high";
  }
  if (risk === "MEDIUM") {
    return "bg-risk-medium/20 text-risk-medium";
  }
  if (risk === "LOW") {
    return "bg-risk-low/15 text-risk-low";
  }
  return "bg-slate-200 text-slate-700";
}

async function resolveRiskLabel(sessionId: string): Promise<OverallRisk | "UNKNOWN"> {
  try {
    const payload = await getGapAnalysis(sessionId);
    if ("status" in payload) {
      return "UNKNOWN";
    }
    return payload.overall_risk;
  } catch {
    return "UNKNOWN";
  }
}

async function buildHistoryGroup(project: InnovationProject): Promise<ProjectHistoryGroup> {
  const sessions = await getProjectSessions(project.id);
  const entries: SessionHistoryItem[] = [];

  for (const session of sessions) {
    entries.push({
      session,
      risk: await resolveRiskLabel(session.id),
    });
  }

  entries.sort(compareSessionDateDesc);
  return { project, entries };
}

export default function SearchHistoryPanel({ open, onClose }: Readonly<SearchHistoryPanelProps>): ReactElement {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [groups, setGroups] = useState<ProjectHistoryGroup[]>([]);

  useEffect(() => {
    if (!open) {
      return;
    }

    setIsLoading(true);
    void (async () => {
      try {
        const projects = await getProjects();
        const grouped = await Promise.all(projects.map(buildHistoryGroup));

        setGroups(grouped.filter((group) => group.entries.length > 0));
      } finally {
        setIsLoading(false);
      }
    })();
  }, [open]);

  const totalSessions = useMemo(
    () => groups.reduce((count, group) => count + group.entries.length, 0),
    [groups],
  );

  const rerunSession = (projectId: string, item: SessionHistoryItem): void => {
    const rerunPayload = {
      project_id: projectId,
      session_id: item.session.id,
      query_text: item.session.query_text,
      cql_generated: item.session.cql_generated,
    };
    globalThis.sessionStorage.setItem("patentpath-rerun-session", JSON.stringify(rerunPayload));
    navigate("/search/new?rerun=1");
    onClose();
  };

  const viewSession = (sessionId: string): void => {
    navigate(`/search/${sessionId}`);
    onClose();
  };

  let body: ReactElement;
  if (isLoading) {
    body = <p className="text-sm text-text-secondary">Loading history...</p>;
  } else if (groups.length === 0) {
    body = <p className="text-sm text-text-secondary">No search sessions found yet.</p>;
  } else {
    body = (
      <div className="space-y-4">
        {groups.map((group) => (
          <section key={group.project.id} className="rounded-xl border border-slate-200 bg-surface p-3">
            <h4 className="text-sm font-semibold text-text-primary">{group.project.title}</h4>
            <div className="mt-2 space-y-2">
              {group.entries.map((entry) => (
                <article key={entry.session.id} className="rounded-lg border border-slate-200 bg-white p-3">
                  <div className="flex items-start justify-between gap-2">
                    <p className="line-clamp-2 text-sm font-medium text-text-primary">{entry.session.query_text}</p>
                    <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${riskBadgeClass(entry.risk)}`}>
                      {entry.risk}
                    </span>
                  </div>

                  <p className="mt-1 text-xs text-text-secondary">
                    {new Date(entry.session.executed_at).toLocaleString()} • {entry.session.result_count} results
                  </p>

                  <div className="mt-2 flex gap-2">
                    <button
                      type="button"
                      onClick={() => rerunSession(group.project.id, entry)}
                      className="rounded-md border border-primary/40 px-2.5 py-1 text-xs font-semibold text-primary hover:bg-primary/5"
                    >
                      Re-run
                    </button>
                    <button
                      type="button"
                      onClick={() => viewSession(entry.session.id)}
                      className="rounded-md bg-primary px-2.5 py-1 text-xs font-semibold text-white hover:bg-blue-900"
                    >
                      View Results
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </section>
        ))}
      </div>
    );
  }

  return (
    <>
      <button
        type="button"
        aria-label="Close search history"
        className={`fixed inset-0 z-40 bg-black/25 transition ${open ? "visible opacity-100" : "invisible opacity-0"}`}
        onClick={onClose}
      />

      <aside
        className={`fixed right-0 top-0 z-50 h-full w-full max-w-xl border-l border-slate-200 bg-white shadow-panel transition-transform duration-300 ${
          open ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-4">
          <div>
            <h3 className="text-base font-semibold text-text-primary">Search History</h3>
            <p className="text-xs text-text-secondary">{totalSessions} sessions across projects</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md border border-slate-300 px-3 py-1 text-xs font-semibold text-text-secondary hover:bg-surface"
          >
            Close
          </button>
        </div>

        <div className="h-[calc(100%-73px)] overflow-y-auto p-4">
          {body}
        </div>
      </aside>
    </>
  );
}
