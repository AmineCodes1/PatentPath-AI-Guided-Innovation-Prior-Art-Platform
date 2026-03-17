/**
 * Project summary card used in dashboard grids.
 */

import type { ReactElement } from "react";
import { useNavigate } from "react-router-dom";
import type { InnovationProject } from "../types/project";

const STATUS_COLOR: Record<InnovationProject["status"], string> = {
  ACTIVE: "bg-risk-low/15 text-risk-low",
  ARCHIVED: "bg-slate-200 text-slate-600",
  REPORT_READY: "bg-accent/20 text-primary",
};

type ProjectCardProps = {
  project: InnovationProject;
};

export default function ProjectCard({ project }: ProjectCardProps): ReactElement {
  const navigate = useNavigate();

  return (
    <button
      type="button"
      onClick={() => navigate(`/project/${project.id}`)}
      className="w-full rounded-2xl border border-slate-200 bg-surface p-5 text-left shadow-panel transition hover:-translate-y-0.5 hover:border-accent"
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="line-clamp-2 text-lg font-semibold text-text-primary">{project.title}</h3>
        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${STATUS_COLOR[project.status]}`}>
          {project.status.replace("_", " ")}
        </span>
      </div>
      <p className="mt-3 line-clamp-3 text-sm text-text-secondary">{project.problem_statement}</p>
      <div className="mt-4 flex items-center justify-between text-xs text-text-secondary">
        <span>{new Date(project.created_at).toLocaleDateString()}</span>
        <span>{project.sessions_count} sessions</span>
      </div>
    </button>
  );
}
