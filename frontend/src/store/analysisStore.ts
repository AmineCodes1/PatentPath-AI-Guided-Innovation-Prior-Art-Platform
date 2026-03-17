/**
 * Zustand store for managing gap analysis lifecycle and feasibility metrics.
 */

import { create } from "zustand";
import {
  getFeasibility,
  pollGapAnalysis,
  triggerGapAnalysis,
} from "../api/analysis";
import type { FeasibilityComplete, GapAnalysis } from "../types/analysis";

type AnalysisStatus = "idle" | "triggering" | "processing" | "complete" | "error";

type AnalysisState = {
  status: AnalysisStatus;
  error: string | null;
  sessionId: string | null;
  gapAnalysis: GapAnalysis | null;
  feasibility: FeasibilityComplete | null;
  lastUpdatedAt: string | null;
  resetAnalysis: () => void;
  runGapAnalysisForSession: (sessionId: string) => Promise<void>;
};

function buildFallbackFeasibility(sessionId: string, gapAnalysis: GapAnalysis): FeasibilityComplete {
  const subScores = [
    gapAnalysis.feasibility_technical,
    gapAnalysis.feasibility_domain,
    gapAnalysis.feasibility_claim,
  ].filter((value): value is number => typeof value === "number");

  const composite = subScores.length > 0
    ? Number((((subScores.reduce((sum, value) => sum + value, 0)) / subScores.length) * 20).toFixed(2))
    : 0;

  return {
    status: "COMPLETE",
    session_id: sessionId,
    technical_readiness: gapAnalysis.feasibility_technical,
    domain_specificity: gapAnalysis.feasibility_domain,
    claim_potential: gapAnalysis.feasibility_claim,
    composite_percentage: composite,
    commentary: gapAnalysis.narrative_text.slice(0, 300),
  };
}

export const useAnalysisStore = create<AnalysisState>((set) => ({
  status: "idle",
  error: null,
  sessionId: null,
  gapAnalysis: null,
  feasibility: null,
  lastUpdatedAt: null,
  resetAnalysis: () => {
    set({
      status: "idle",
      error: null,
      sessionId: null,
      gapAnalysis: null,
      feasibility: null,
      lastUpdatedAt: null,
    });
  },
  runGapAnalysisForSession: async (sessionId) => {
    set({
      status: "triggering",
      error: null,
      sessionId,
      gapAnalysis: null,
      feasibility: null,
      lastUpdatedAt: null,
    });

    try {
      await triggerGapAnalysis(sessionId);
    } catch {
      // If the backend has already queued processing, polling may still complete successfully.
    }

    set({ status: "processing" });

    try {
      const analysis = await pollGapAnalysis(sessionId);
      const feasibilityResponse = await getFeasibility(sessionId);
      const feasibility = feasibilityResponse.status === "COMPLETE"
        ? feasibilityResponse
        : buildFallbackFeasibility(sessionId, analysis);

      set({
        status: "complete",
        error: null,
        gapAnalysis: analysis,
        feasibility,
        lastUpdatedAt: new Date().toISOString(),
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to run gap analysis.";
      set({
        status: "error",
        error: message,
      });
    }
  },
}));
