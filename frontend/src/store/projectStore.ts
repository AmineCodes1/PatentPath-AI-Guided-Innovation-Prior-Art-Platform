/**
 * Zustand store for project list and active project context.
 */

import { create } from "zustand";
import {
  archiveProject as archiveProjectApi,
  createNote as createNoteApi,
  createProject as createProjectApi,
  deleteNote as deleteNoteApi,
  getProject as getProjectApi,
  getProjectNotes as getProjectNotesApi,
  getProjectRiskTrend as getProjectRiskTrendApi,
  getProjectSessions as getProjectSessionsApi,
  getProjectTimeline as getProjectTimelineApi,
  getProjects as getProjectsApi,
  updateProject as updateProjectApi,
} from "../api/projects";
import type {
  InnovationProject,
  ProjectCreatePayload,
  ProjectNote,
  ProjectNoteCreatePayload,
  ProjectRiskTrendPoint,
  ProjectSessionSummary,
  ProjectTimelineEvent,
  ProjectUpdatePayload,
} from "../types/project";

type ProjectState = {
  projects: InnovationProject[];
  currentProject: InnovationProject | null;
  currentProjectSessions: ProjectSessionSummary[];
  currentProjectTimeline: ProjectTimelineEvent[];
  currentProjectNotes: ProjectNote[];
  currentProjectRiskTrend: ProjectRiskTrendPoint[];
  isLoading: boolean;
  error: string | null;
  fetchProjects: () => Promise<void>;
  fetchProjectWorkspace: (projectId: string) => Promise<void>;
  fetchProjectTimeline: (projectId: string) => Promise<void>;
  fetchProjectNotes: (projectId: string) => Promise<void>;
  fetchProjectRiskTrend: (projectId: string) => Promise<void>;
  createProjectNote: (projectId: string, payload: ProjectNoteCreatePayload) => Promise<ProjectNote | null>;
  deleteProjectNote: (projectId: string, noteId: string) => Promise<boolean>;
  updateProject: (projectId: string, payload: ProjectUpdatePayload) => Promise<InnovationProject | null>;
  archiveProject: (projectId: string) => Promise<InnovationProject | null>;
  createProject: (payload: ProjectCreatePayload) => Promise<InnovationProject | null>;
  setCurrentProject: (project: InnovationProject | null) => void;
};

export const useProjectStore = create<ProjectState>((set, get) => ({
  projects: [],
  currentProject: null,
  currentProjectSessions: [],
  currentProjectTimeline: [],
  currentProjectNotes: [],
  currentProjectRiskTrend: [],
  isLoading: false,
  error: null,
  fetchProjects: async () => {
    set({ isLoading: true, error: null });
    try {
      const projects = await getProjectsApi();
      set({ projects, isLoading: false });
      const { currentProject } = get();
      if (currentProject) {
        const updatedCurrent = projects.find((item) => item.id === currentProject.id) ?? null;
        set({ currentProject: updatedCurrent });
      }
    } catch {
      set({ error: "Failed to load projects.", isLoading: false });
    }
  },
  fetchProjectWorkspace: async (projectId) => {
    set({ isLoading: true, error: null });
    try {
      const [project, sessions, timeline, notes, trend] = await Promise.all([
        getProjectApi(projectId),
        getProjectSessionsApi(projectId),
        getProjectTimelineApi(projectId),
        getProjectNotesApi(projectId),
        getProjectRiskTrendApi(projectId),
      ]);

      set((state) => ({
        currentProject: project,
        currentProjectSessions: sessions,
        currentProjectTimeline: timeline,
        currentProjectNotes: notes,
        currentProjectRiskTrend: trend,
        projects: state.projects.some((item) => item.id === project.id)
          ? state.projects.map((item) => (item.id === project.id ? project : item))
          : [project, ...state.projects],
        isLoading: false,
      }));
    } catch {
      set({ error: "Failed to load project workspace.", isLoading: false });
    }
  },
  fetchProjectTimeline: async (projectId) => {
    try {
      const timeline = await getProjectTimelineApi(projectId);
      set({ currentProjectTimeline: timeline });
    } catch {
      set({ error: "Failed to load project timeline." });
    }
  },
  fetchProjectNotes: async (projectId) => {
    try {
      const notes = await getProjectNotesApi(projectId);
      set({ currentProjectNotes: notes });
    } catch {
      set({ error: "Failed to load project notes." });
    }
  },
  fetchProjectRiskTrend: async (projectId) => {
    try {
      const trend = await getProjectRiskTrendApi(projectId);
      set({ currentProjectRiskTrend: trend });
    } catch {
      set({ error: "Failed to load project risk trend." });
    }
  },
  createProjectNote: async (projectId, payload) => {
    try {
      const note = await createNoteApi(projectId, payload);
      set((state) => ({ currentProjectNotes: [note, ...state.currentProjectNotes] }));
      return note;
    } catch {
      set({ error: "Failed to create note." });
      return null;
    }
  },
  deleteProjectNote: async (projectId, noteId) => {
    try {
      await deleteNoteApi(projectId, noteId);
      set((state) => ({
        currentProjectNotes: state.currentProjectNotes.filter((item) => item.id !== noteId),
      }));
      return true;
    } catch {
      set({ error: "Failed to delete note." });
      return false;
    }
  },
  updateProject: async (projectId, payload) => {
    try {
      const updated = await updateProjectApi(projectId, payload);
      set((state) => ({
        currentProject: updated,
        projects: state.projects.map((item) => (item.id === updated.id ? updated : item)),
      }));
      return updated;
    } catch {
      set({ error: "Failed to update project." });
      return null;
    }
  },
  archiveProject: async (projectId) => {
    try {
      const archived = await archiveProjectApi(projectId);
      set((state) => ({
        currentProject: state.currentProject?.id === archived.id ? archived : state.currentProject,
        projects: state.projects.map((item) => (item.id === archived.id ? archived : item)),
      }));
      return archived;
    } catch {
      set({ error: "Failed to archive project." });
      return null;
    }
  },
  createProject: async (payload) => {
    set({ isLoading: true, error: null });
    try {
      const created = await createProjectApi(payload);
      set((state) => ({
        projects: [created, ...state.projects],
        currentProject: created,
        isLoading: false,
      }));
      return created;
    } catch {
      set({ error: "Failed to create project.", isLoading: false });
      return null;
    }
  },
  setCurrentProject: (project) => set({ currentProject: project }),
}));
