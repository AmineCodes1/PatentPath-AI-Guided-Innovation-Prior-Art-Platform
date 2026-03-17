/**
 * Typed API methods for gap analysis and feasibility polling.
 */

import apiClient from "./client";
import type {
  FeasibilityResponse,
  GapAnalysis,
  GapAnalysisResponse,
  TriggerGapAnalysisResponse,
} from "../types/analysis";

export async function triggerGapAnalysis(sessionId: string): Promise<TriggerGapAnalysisResponse> {
  const response = await apiClient.post<TriggerGapAnalysisResponse>(
    `/analysis/session/${sessionId}/gap-analysis`,
  );
  return response.data;
}

export async function getGapAnalysis(sessionId: string): Promise<GapAnalysisResponse> {
  const response = await apiClient.get<GapAnalysisResponse>(`/analysis/session/${sessionId}/gap-analysis`);
  return response.data;
}

export async function getFeasibility(sessionId: string): Promise<FeasibilityResponse> {
  const response = await apiClient.get<FeasibilityResponse>(`/analysis/session/${sessionId}/feasibility`);
  return response.data;
}

export async function pollGapAnalysis(
  sessionId: string,
  options?: {
    intervalMs?: number;
    maxAttempts?: number;
    onTick?: (attempt: number) => void;
  },
): Promise<GapAnalysis> {
  const intervalMs = options?.intervalMs ?? 2500;
  const maxAttempts = options?.maxAttempts ?? 48;

  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    options?.onTick?.(attempt);
    const payload = await getGapAnalysis(sessionId);

    if (!("status" in payload)) {
      return payload;
    }

    await new Promise<void>((resolve) => {
      window.setTimeout(resolve, intervalMs);
    });
  }

  throw new Error("Gap analysis timed out while processing.");
}
