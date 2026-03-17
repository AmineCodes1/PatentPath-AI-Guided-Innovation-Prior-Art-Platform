/**
 * Typed API methods for innovation projects.
 */

import apiClient from "./client";
import type {
  InnovationProject,
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
