/**
 * Collapsible project tree sidebar with quick project switching and creation action.
 */

import type { ReactElement } from "react";
import type { InnovationProject } from "../../types/project";

type ProjectSidebarProps = {
  projects: InnovationProject[];
  activeProjectId: string;
  collapsed: boolean;
  onToggleCollapsed: () => void;
  onSelectProject: (projectId: string) => void;
  onCreateProject: () => void;
};

export default function ProjectSidebar({
  projects,
  activeProjectId,
  collapsed,
  onToggleCollapsed,
  onSelectProject,
  onCreateProject,
}: Readonly<ProjectSidebarProps>): ReactElement {
  return (
    <aside className={`rounded-2xl border border-slate-200 bg-white p-4 shadow-panel ${collapsed ? "h-16" : ""}`}>
      <div className="flex items-center justify-between gap-2">
        <h2 className="text-sm font-semibold uppercase tracking-widest text-primary">Projects</h2>
        <button
          type="button"
          onClick={onToggleCollapsed}
          className="text-xs font-medium text-accent"
        >
          {collapsed ? "Expand" : "Collapse"}
        </button>
      </div>

      {collapsed ? null : (
        <>
          <button
            type="button"
            onClick={onCreateProject}
            className="mt-3 w-full rounded-lg bg-primary px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-900"
          >
            New Project
          </button>

          <div className="mt-3 space-y-2">
            {projects.map((project) => (
              <button
                type="button"
                key={project.id}
                onClick={() => onSelectProject(project.id)}
                className={`w-full rounded-lg px-3 py-2 text-left text-sm transition ${
                  activeProjectId === project.id
                    ? "bg-accent text-white"
                    : "bg-surface text-text-primary hover:bg-accent/20"
                }`}
              >
                <p className="truncate font-medium">{project.title}</p>
                <p className="mt-0.5 text-xs opacity-80">{project.status.replace("_", " ")}</p>
              </button>
            ))}
          </div>
        </>
      )}
    </aside>
  );
}
