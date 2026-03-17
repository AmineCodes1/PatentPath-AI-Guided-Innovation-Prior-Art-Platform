/**
 * Typed API methods for innovation projects.
 */

import apiClient from "./client";
import type {
  InnovationProject,
  ProjectNote,
  ProjectNoteCreatePayload,
  ProjectRiskTrendPoint,
  ProjectSessionSummary,
  ProjectTimelineEvent,
  ProjectCreatePayload,
  ProjectUpdatePayload,
} from "../types/project";

export async function getProjects(): Promise<InnovationProject[]> {
  const response = await apiClient.get<InnovationProject[]>("/projects");
  return response.data;
}

export async function getProject(id: string): Promise<InnovationProject> {
  const response = await apiClient.get<InnovationProject>(`/projects/${id}`);
  return response.data;
}

export async function createProject(data: ProjectCreatePayload): Promise<InnovationProject> {
  const response = await apiClient.post<InnovationProject>("/projects", data);
  return response.data;
}

export async function updateProject(
  id: string,
  data: ProjectUpdatePayload,
): Promise<InnovationProject> {
  const response = await apiClient.put<InnovationProject>(`/projects/${id}`, data);
  return response.data;
}

export async function archiveProject(id: string): Promise<InnovationProject> {
  const response = await apiClient.delete<InnovationProject>(`/projects/${id}`);
  return response.data;
}

export async function getProjectSessions(id: string): Promise<ProjectSessionSummary[]> {
  const response = await apiClient.get<ProjectSessionSummary[]>(`/projects/${id}/sessions`);
  return response.data;
}

export async function getProjectTimeline(id: string): Promise<ProjectTimelineEvent[]> {
  const response = await apiClient.get<ProjectTimelineEvent[]>(`/projects/${id}/timeline`);
  return response.data;
}

export async function getProjectRiskTrend(id: string): Promise<ProjectRiskTrendPoint[]> {
  const response = await apiClient.get<ProjectRiskTrendPoint[]>(`/projects/${id}/risk-trend`);
  return response.data;
}

export async function getProjectNotes(id: string): Promise<ProjectNote[]> {
  const response = await apiClient.get<ProjectNote[]>(`/projects/${id}/notes`);
  return response.data;
}

export async function createNote(
  projectId: string,
  data: ProjectNoteCreatePayload,
): Promise<ProjectNote> {
  const response = await apiClient.post<ProjectNote>(`/projects/${projectId}/notes`, data);
  return response.data;
}

export async function deleteNote(projectId: string, noteId: string): Promise<void> {
  await apiClient.delete(`/projects/${projectId}/notes/${noteId}`);
}
