/**
 * Search workflow and result-related frontend types.
 */

export type RiskLabel = "HIGH" | "MEDIUM" | "LOW" | "MINIMAL";

export type DateRangeFilter = {
  date_from?: string;
  date_to?: string;
};

export type SearchFilters = {
  date_from?: string;
  date_to?: string;
  country_codes: string[];
  ipc_classes: string[];
  applicant?: string;
  legal_status?: string;
};

export type SearchPreviewResponse = {
  cql_generated: string;
  keywords_extracted: string[];
  ipc_suggestions: string[];
  is_valid: boolean;
  validation_error?: string;
  metadata?: Record<string, string>;
};

export type PatentRecordSummary = {
  publication_number: string;
  title: string;
  abstract: string;
  applicants: string[];
  publication_date: string;
  espacenet_url: string;
  legal_status?: string;
};

export type ScoredResult = {
  patent: PatentRecordSummary;
  bm25_score: number;
  tfidf_cosine: number;
  semantic_cosine: number;
  composite_score: number;
  risk_label: RiskLabel;
  rank: number;
};

export type SearchResultsResponse = {
  session_id: string;
  total_count: number;
  results: ScoredResult[];
};

export type ExecuteSearchResponse = {
  session_id: string;
  status: "PENDING";
  estimated_seconds: number;
};
