/**
 * Dashboard page with project overview and recent search history.
 */

import { useEffect, useMemo, useState } from "react";
import TopNav from "../components/layout/TopNav";
import Footer from "../components/layout/Footer";
import type { ReactElement } from "react";
import ProjectCard from "../components/ProjectCard";
import EmptyState from "../components/common/EmptyState";
import { useProjectStore } from "../store/projectStore";
import type { RecentSearch } from "../types/project";

function mockRecentSearches(projectIds: string[]): RecentSearch[] {
  const now = Date.now();
  return projectIds.slice(0, 5).map((projectId, index) => ({
    id: `${projectId}-${index}`,
    project_id: projectId,
    query_text: `Adaptive control for project ${projectId.slice(0, 6)}`,
    result_count: 18 - index,
    status: "COMPLETE",
    executed_at: new Date(now - index * 1000 * 60 * 60 * 10).toISOString(),
  }));
}

export default function DashboardPage(): ReactElement {
  const projects = useProjectStore((state) => state.projects);
  const isLoading = useProjectStore((state) => state.isLoading);
  const fetchProjects = useProjectStore((state) => state.fetchProjects);
  const createProject = useProjectStore((state) => state.createProject);

  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    void fetchProjects();
  }, [fetchProjects]);

  const recentSearches = useMemo(() => mockRecentSearches(projects.map((item) => item.id)), [projects]);

  const handleCreateProject = async (): Promise<void> => {
    setIsCreating(true);
    await createProject({
      title: "New Innovation Project",
      problem_statement:
        "Describe the technical challenge, constraints, and intended advantages to begin searching prior art.",
      domain_ipc_class: "G06F",
    });
    setIsCreating(false);
  };

  return (
    <div className="min-h-screen bg-surface">
      <TopNav />
      <main className="mx-auto max-w-7xl px-6 py-8">
        <section className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-text-primary">Your Innovation Projects</h1>
            <p className="mt-2 text-text-secondary">Track active ideas, run prior art searches, and iterate faster.</p>
          </div>
          <button
            type="button"
            onClick={() => void handleCreateProject()}
            disabled={isCreating}
            className="rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-900 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isCreating ? "Creating..." : "New Project"}
          </button>
        </section>

        <section className="mt-8">
          {isLoading ? <p className="text-sm text-text-secondary">Loading projects...</p> : null}
          {!isLoading && projects.length === 0 ? (
            <EmptyState
              variant="no-projects"
              title="No projects yet"
              subtitle="Start with your first invention idea and let PatentPath guide the prior art workflow."
              steps={["Describe your idea", "Search prior art", "Get your report"]}
              actionLabel="Create first project"
              onAction={() => void handleCreateProject()}
            />
          ) : null}

          {projects.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {projects.map((project) => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </div>
          ) : null}
        </section>

        <section className="mt-10 rounded-2xl border border-slate-200 bg-white p-6 shadow-panel">
          <h2 className="text-lg font-semibold text-text-primary">Recent Searches</h2>
          <div className="mt-4 divide-y divide-slate-100">
            {recentSearches.length === 0 ? (
              <p className="py-4 text-sm text-text-secondary">No searches yet.</p>
            ) : (
              recentSearches.slice(0, 5).map((entry) => (
                <div key={entry.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
                  <div>
                    <p className="text-sm font-medium text-text-primary">{entry.query_text}</p>
                    <p className="text-xs text-text-secondary">
                      {new Date(entry.executed_at).toLocaleString()} • {entry.result_count} results
                    </p>
                  </div>
                  <span className="rounded-full bg-accent/20 px-3 py-1 text-xs font-semibold text-primary">
                    {entry.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
