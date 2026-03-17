/**
 * Gap analysis and feasibility frontend type models.
 */

export type OverallRisk = "HIGH" | "MEDIUM" | "LOW";

export type GapAnalysis = {
  id: string;
  session_id: string;
  overall_risk: OverallRisk;
  covered_aspects: string[];
  gap_aspects: string[];
  suggestions: string[];
  narrative_text: string;
  model_used: string;
  generated_at: string;
  feasibility_technical: number | null;
  feasibility_domain: number | null;
  feasibility_claim: number | null;
};

export type GapAnalysisProcessing = {
  status: "PROCESSING";
};

export type GapAnalysisResponse = GapAnalysis | GapAnalysisProcessing;

export type TriggerGapAnalysisResponse = {
  job_id: string;
  status: "PENDING";
};

export type FeasibilityProcessing = {
  status: "PROCESSING";
};

export type FeasibilityComplete = {
  status: "COMPLETE";
  session_id: string;
  technical_readiness: number | null;
  domain_specificity: number | null;
  claim_potential: number | null;
  composite_percentage: number;
  commentary: string;
};

export type FeasibilityResponse = FeasibilityComplete | FeasibilityProcessing;
