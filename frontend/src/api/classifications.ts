/**
 * IPC classification API helpers for browse and search interactions.
 */

import apiClient from "./client";

export type IPCClass = {
  code: string;
  title: string;
  description: string;
  keywords: string[];
};

export type IPCSection = {
  section: string;
  title: string;
  classes: IPCClass[];
};

export type IPCTreeResponse = {
  sections: IPCSection[];
};

export async function getIPCTree(): Promise<IPCTreeResponse> {
  const response = await apiClient.get<IPCTreeResponse>("/classifications/ipc");
  return response.data;
}

export async function searchIPC(query: string): Promise<IPCClass[]> {
  const normalized = query.trim();
  if (!normalized) {
    return [];
  }
  const response = await apiClient.get<IPCClass[]>("/classifications/ipc/search", {
    params: { q: normalized },
  });
  return response.data;
}

export async function getIPCClass(code: string): Promise<IPCClass> {
  const response = await apiClient.get<IPCClass>(`/classifications/ipc/${encodeURIComponent(code.trim())}`);
  return response.data;
}
