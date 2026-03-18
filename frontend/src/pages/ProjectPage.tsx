/**
 * Full project workspace page with tabbed views for searches, timeline, notes, and settings.
 */

import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import type { ReactElement } from "react";
import Footer from "../components/layout/Footer";
import TopNav from "../components/layout/TopNav";
import NotesTab from "../components/project/NotesTab";
import ProjectSettingsTab from "../components/project/ProjectSettingsTab";
import ProjectSidebar from "../components/project/ProjectSidebar";
import SearchHistoryTab from "../components/project/SearchHistoryTab";
import TimelineTab from "../components/project/TimelineTab";
import { useProjectStore } from "../store/projectStore";
import { useReportStore } from "../store/reportStore";
import type { ProjectUpdatePayload } from "../types/project";

type WorkspaceTab = "Searches" | "Timeline" | "Notes" | "Settings";

const STATUS_STYLE = {
  ACTIVE: "bg-risk-low/15 text-risk-low",
  ARCHIVED: "bg-slate-200 text-slate-700",
  REPORT_READY: "bg-accent/20 text-primary",
} as const;

export default function ProjectPage(): ReactElement {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const projects = useProjectStore((state) => state.projects);
  const currentProject = useProjectStore((state) => state.currentProject);
  const currentProjectSessions = useProjectStore((state) => state.currentProjectSessions);
  const currentProjectTimeline = useProjectStore((state) => state.currentProjectTimeline);
  const currentProjectNotes = useProjectStore((state) => state.currentProjectNotes);
  const currentProjectRiskTrend = useProjectStore((state) => state.currentProjectRiskTrend);
  const fetchProjects = useProjectStore((state) => state.fetchProjects);
  const fetchProjectWorkspace = useProjectStore((state) => state.fetchProjectWorkspace);
  const createProject = useProjectStore((state) => state.createProject);
  const createProjectNote = useProjectStore((state) => state.createProjectNote);
  const deleteProjectNote = useProjectStore((state) => state.deleteProjectNote);
  const updateProject = useProjectStore((state) => state.updateProject);
  const archiveProject = useProjectStore((state) => state.archiveProject);
  const completedReports = useReportStore((state) => state.completedReports);
  const downloadCompletedReport = useReportStore((state) => state.downloadCompletedReport);

  const [activeTab, setActiveTab] = useState<WorkspaceTab>("Searches");
  const [collapsedSidebar, setCollapsedSidebar] = useState(false);
  const [editingTitle, setEditingTitle] = useState(false);
  const [draftTitle, setDraftTitle] = useState("");

  useEffect(() => {
    void fetchProjects();
  }, [fetchProjects]);

  useEffect(() => {
    if (!id) {
      return;
    }
    void fetchProjectWorkspace(id);
  }, [fetchProjectWorkspace, id]);

  useEffect(() => {
    if (currentProject) {
      setDraftTitle(currentProject.title);
    }
  }, [currentProject]);

  const saveInlineTitle = async (): Promise<void> => {
    if (!id || !currentProject) {
      return;
    }
    if (!draftTitle.trim() || draftTitle.trim() === currentProject.title) {
      setEditingTitle(false);
      return;
    }
    await updateProject(id, { title: draftTitle.trim() });
    setEditingTitle(false);
  };

  const handleCreateProject = async (): Promise<void> => {
    const created = await createProject({
      title: "New Innovation Project",
      problem_statement:
        "Describe the technical challenge, constraints, and intended advantages to begin searching prior art.",
      domain_ipc_class: "G06F",
    });
    if (created) {
      navigate(`/project/${created.id}`);
    }
  };

  const handleSaveSettings = async (payload: ProjectUpdatePayload): Promise<void> => {
    if (!id) {
      return;
    }
    await updateProject(id, payload);
  };

  const handleArchiveProject = async (): Promise<void> => {
    if (!id) {
      return;
    }
    await archiveProject(id);
  };

  const handleCreateNote = async (payload: { title: string; content: string; linked_session_id?: string }): Promise<void> => {
    if (!id) {
      return;
    }
    await createProjectNote(id, payload);
  };

  const handleDeleteNote = async (noteId: string): Promise<void> => {
    if (!id) {
      return;
    }
    await deleteProjectNote(id, noteId);
  };

  const handleRerunSearch = (sessionId: string): void => {
    navigate(`/search/${sessionId}`);
  };

  const handleViewResults = (sessionId: string): void => {
    navigate(`/search/${sessionId}`);
  };

  const openNewSearch = (): void => {
    navigate("/search/new");
  };

  const selectedProjectId = currentProject?.id ?? id ?? "";

  const reportsForProject = useMemo(
    () => completedReports.filter((item) => item.project_id === selectedProjectId),
    [completedReports, selectedProjectId],
  );

  const sessionDateById = useMemo(() => {
    return currentProjectSessions.reduce<Record<string, string>>((accumulator, session) => {
      accumulator[session.id] = session.executed_at;
      return accumulator;
    }, {});
  }, [currentProjectSessions]);

  return (
    <div className="min-h-screen bg-surface">
      <TopNav />
      <main className="mx-auto grid max-w-[1400px] grid-cols-1 gap-5 px-4 py-6 xl:grid-cols-[280px_minmax(0,1fr)]">
        <ProjectSidebar
          projects={projects}
          activeProjectId={selectedProjectId}
          collapsed={collapsedSidebar}
          onToggleCollapsed={() => setCollapsedSidebar((value) => !value)}
          onSelectProject={(projectId) => navigate(`/project/${projectId}`)}
          onCreateProject={() => void handleCreateProject()}
        />

        <section className="space-y-5">
          <header className="rounded-2xl border border-slate-200 bg-white p-5 shadow-panel">
            {currentProject ? (
              <>
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    {editingTitle ? (
                      <input
                        type="text"
                        value={draftTitle}
                        onChange={(event) => setDraftTitle(event.target.value)}
                        onBlur={() => void saveInlineTitle()}
                        onKeyDown={(event) => {
                          if (event.key === "Enter") {
                            void saveInlineTitle();
                          }
                        }}
                        autoFocus
                        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-2xl font-bold text-text-primary outline-none focus:border-accent"
                      />
                    ) : (
                      <button
                        type="button"
                        onClick={() => setEditingTitle(true)}
                        className="text-left text-2xl font-bold text-text-primary"
                      >
                        {currentProject.title}
                      </button>
                    )}
                    <p className="mt-2 max-w-3xl text-sm text-text-secondary">
                      {currentProject.problem_statement}
                    </p>
                    <p className="mt-2 text-xs font-semibold uppercase tracking-widest text-accent">
                      IPC Domain: {currentProject.domain_ipc_class ?? "Not set"}
                    </p>
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${STATUS_STYLE[currentProject.status]}`}>
                      {currentProject.status.replace("_", " ")}
                    </span>
                    <button
                      type="button"
                      onClick={openNewSearch}
                      className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-900"
                    >
                      New Search
                    </button>
                  </div>
                </div>

                <nav className="mt-4 flex flex-wrap gap-2">
                  {(["Searches", "Timeline", "Notes", "Settings"] as WorkspaceTab[]).map((tab) => (
                    <button
                      type="button"
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`rounded-lg px-3 py-2 text-sm font-medium transition ${
                        activeTab === tab ? "bg-primary text-white" : "bg-surface text-text-secondary hover:bg-accent/20"
                      }`}
                    >
                      {tab}
                    </button>
                  ))}
                </nav>

                <div className="mt-4 rounded-xl border border-slate-200 bg-surface p-3">
                  <h3 className="text-sm font-semibold text-text-primary">Reports</h3>
                  {reportsForProject.length === 0 ? (
                    <p className="mt-2 text-xs text-text-secondary">No generated reports for this project yet.</p>
                  ) : (
                    <div className="mt-2 space-y-2">
                      {reportsForProject.map((report) => {
                        const sessionDate = sessionDateById[report.session_id] ?? report.session_date;
                        const viewedText = report.viewed_at
                          ? new Date(report.viewed_at).toLocaleString()
                          : "Not viewed";

                        return (
                          <div
                            key={report.job_id}
                            className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2"
                          >
                            <div>
                              <p className="text-xs font-semibold text-text-primary">
                                Session: {new Date(sessionDate).toLocaleString()}
                              </p>
                              <p className="text-[11px] text-text-secondary">
                                Viewed: {viewedText}
                              </p>
                            </div>
                            <button
                              type="button"
                              onClick={() => void downloadCompletedReport(report.job_id)}
                              className="rounded-md bg-primary px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-blue-900"
                            >
                              Download
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </>
            ) : (
              <p className="text-sm text-text-secondary">Loading project workspace...</p>
            )}
          </header>

          {currentProject ? (
            <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-panel">
              {activeTab === "Searches" ? (
                <SearchHistoryTab
                  sessions={currentProjectSessions}
                  timeline={currentProjectTimeline}
                  onRerunSearch={handleRerunSearch}
                  onViewResults={handleViewResults}
                />
              ) : null}

              {activeTab === "Timeline" ? (
                <TimelineTab
                  events={currentProjectTimeline}
                  riskTrend={currentProjectRiskTrend}
                />
              ) : null}

              {activeTab === "Notes" ? (
                <NotesTab
                  notes={currentProjectNotes}
                  sessions={currentProjectSessions}
                  onCreateNote={handleCreateNote}
                  onDeleteNote={handleDeleteNote}
                />
              ) : null}

              {activeTab === "Settings" ? (
                <ProjectSettingsTab
                  project={currentProject}
                  onSave={handleSaveSettings}
                  onArchive={handleArchiveProject}
                />
              ) : null}
            </article>
          ) : null}
        </section>
      </main>
      <Footer />
    </div>
  );
}
