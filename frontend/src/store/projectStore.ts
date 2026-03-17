/**
 * Zustand store for project list and active project context.
 */

import { create } from "zustand";
import {
  createProject as createProjectApi,
  getProjects as getProjectsApi,
} from "../api/projects";
import type { InnovationProject, ProjectCreatePayload } from "../types/project";

type ProjectState = {
  projects: InnovationProject[];
  currentProject: InnovationProject | null;
  isLoading: boolean;
  error: string | null;
  fetchProjects: () => Promise<void>;
  createProject: (payload: ProjectCreatePayload) => Promise<InnovationProject | null>;
  setCurrentProject: (project: InnovationProject | null) => void;
};

export const useProjectStore = create<ProjectState>((set, get) => ({
  projects: [],
  currentProject: null,
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
